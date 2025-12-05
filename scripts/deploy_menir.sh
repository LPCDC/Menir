#!/usr/bin/env bash
set -euo pipefail

# MENIR v10.3 — UNIVERSAL DEPLOY SCRIPT (SANITIZED)
# This script installs dependencies, prepares a virtualenv, starts the MCP server,
# optionally runs the CLI test and the voice setup. It DOES NOT contain any
# hard-coded API keys. You must provide OPENAI_API_KEY via environment or a
# secure prompt.

usage() {
  cat <<EOF
Usage: $(basename "$0") [--no-apt] [--no-voice] [--no-cli] [--openai-key KEY]

Options:
  --no-apt        Skip apt-get package installation (useful in CI/container)
  --no-voice      Skip running voice setup script
  --no-cli        Skip running the ask_menir CLI test
  --openai-key KEY  Provide OpenAI API key on command line (not recommended)
  -h, --help      Show this help and exit

Example:
  OPENAI_API_KEY="sk-..." ./scripts/deploy_menir.sh
  or
  ./scripts/deploy_menir.sh --openai-key-file /path/to/secret

This script will NOT store secrets in the repository. For CI, set the
OPENAI_API_KEY environment variable in your CI settings.
EOF
}

NO_APT=0
NO_VOICE=0
NO_CLI=0
OPENAI_KEY_INPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-apt) NO_APT=1; shift ;;
    --no-voice) NO_VOICE=1; shift ;;
    --no-cli) NO_CLI=1; shift ;;
    --openai-key) OPENAI_KEY_INPUT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

REPO_DIR="$(pwd)"
echo "📁 Working in: ${REPO_DIR}"

# 1. Optional: install system packages
if [ "$NO_APT" -eq 0 ]; then
  if command -v apt-get >/dev/null 2>&1; then
    echo "🔧 Installing system packages (requires sudo)..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-venv python3-pip portaudio19-dev ffmpeg git curl build-essential || true
  else
    echo "⚠️ apt-get not found; skipping system package install"
  fi
else
  echo "ℹ️ Skipping apt-get installation (--no-apt)"
fi

# 2. Create & activate virtualenv
if [ ! -d ".venv" ]; then
  echo "🐍 Creating virtualenv .venv"
  python3 -m venv .venv
fi
source .venv/bin/activate

# 3. Install Python requirements
echo "📦 Installing Python packages from requirements.txt"
python -m pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
else
  echo "⚠️ requirements.txt not found; please create one before continuing"
fi

# 4. Ensure OPENAI_API_KEY is available (do NOT hardcode secrets)
if [ -n "$OPENAI_KEY_INPUT" ]; then
  export OPENAI_API_KEY="$OPENAI_KEY_INPUT"
  echo "🔒 Using OpenAI key provided on command line (be careful: this can be insecure)"
fi

if [ -z "${OPENAI_API_KEY:-}" ]; then
  # Interactive prompt (masked) if running in a TTY
  if [ -t 0 ]; then
    echo -n "🔑 OPENAI_API_KEY not set. Enter it now (input hidden) or press ENTER to skip: "
    # read -s into variable
    read -rs INPUT_KEY || true
    echo
    if [ -n "$INPUT_KEY" ]; then
      export OPENAI_API_KEY="$INPUT_KEY"
      echo "🔒 OPENAI_API_KEY set for this session"
    else
      echo "ℹ️ Proceeding without OPENAI_API_KEY — CLI GPT calls will be skipped or will error"
    fi
  else
    echo "ℹ️ No OPENAI_API_KEY in env and not interactive. CLI GPT calls will be skipped"
  fi
else
  echo "🔒 OPENAI_API_KEY found in environment"
fi

# 5. Start MCP server
if lsof -i:8080 >/dev/null 2>&1; then
  echo "⚠️ Port 8080 already in use. Skipping MCP startup."
else
  echo "🚀 Starting MCP JSON-RPC Server on :8080"
  mkdir -p logs
  nohup python -m uvicorn menir10.mcp_app:app --host 0.0.0.0 --port 8080 &> logs/mcp_server.log &
  echo "📝 Server logs: logs/mcp_server.log"
fi

sleep 2

# 6. Smoke test: ping
echo "🧪 Testing MCP /health and JSON-RPC ping"
curl -sS http://localhost:8080/health || true
curl -sS -X POST http://localhost:8080/jsonrpc -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"ping","id":1}' || true

# 7. Optional CLI test (only if OPENAI_API_KEY is set)
if [ "$NO_CLI" -eq 0 ]; then
  if [ -n "${OPENAI_API_KEY:-}" ]; then
    echo "💬 Running ask_menir.py CLI test (will call OpenAI)"
    python3 ask_menir.py ask "Summarize current state" -p itau_15220012 || true
  else
    echo "⚠️ Skipping CLI GPT test because OPENAI_API_KEY is not set"
  fi
else
  echo "ℹ️ Skipping CLI test (--no-cli)"
fi

# 8. Optional voice setup
if [ "$NO_VOICE" -eq 0 ]; then
  if [ -x ./setup_menir_voice.sh ]; then
    echo "🎤 Running voice setup script..."
    bash ./setup_menir_voice.sh || echo "⚠️ Voice setup had issues; check logs"
  else
    echo "⚠️ setup_menir_voice.sh not found or not executable; skipping voice setup"
  fi
else
  echo "ℹ️ Skipping voice setup (--no-voice)"
fi

echo "✅ MENIR v10.3 deploy script finished (no secrets written to disk)."

exit 0
