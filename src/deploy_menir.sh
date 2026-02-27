#!/bin/bash
set -euo pipefail

# ────── ENVIRONMENT SETUP ──────
echo "🔧 [1/7] Installing dependencies..."
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt

# ────── OPENAI KEY ──────
if [ -z "${OPENAI_API_KEY:-}" ]; then
  read -p "🔐 Enter your OpenAI API key: " OPENAI_API_KEY
  export OPENAI_API_KEY
fi

# ────── START MCP SERVER ──────
echo "🚀 [2/7] Starting MCP FastAPI server..."
nohup uvicorn menir10.mcp_app:app --host 0.0.0.0 --port 8080 > mcp.log 2>&1 &
sleep 2

# ────── TEST MCP PING ──────
echo "📡 [3/7] Verifying MCP ping..."
curl -s http://localhost:8080/health | grep 'OK' || (echo "❌ MCP Health Check Failed" && exit 1)

# ────── TEST CLI with Project "itau_15220012" ──────
echo "🧠 [4/7] Testing ask_menir.py on Itaú..."
python ask_menir.py ask "Qual o status atual?" -p itau_15220012 || echo "⚠️ CLI GPT test failed (OK if key was wrong)"

# ────── VOICE SETUP (Optional) ──────
echo "🎙️ [5/7] Setting up voice interface..."
if [ -f setup_menir_voice.sh ]; then
  chmod +x setup_menir_voice.sh && ./setup_menir_voice.sh --auto || echo "⚠️ Voice setup failed/skipped"
fi

# ────── PACKAGE (Redistribution) ──────
echo "📦 [6/7] Creating redistributable package..."
mkdir -p dist && tar -czf dist/menir103_package.tar.gz menir10/ voice/ ask_menir.py deploy_menir.sh requirements.txt

# ────── DONE ──────
echo "✅ [7/7] Deployment complete."
echo "🎯 Server running on http://localhost:8080"
echo "🗂️ Package available at dist/menir103_package.tar.gz"

