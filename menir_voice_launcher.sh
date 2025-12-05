#!/bin/bash

# Menir Voice Launcher - All-in-one startup script

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VOICE_DIR="${PROJECT_ROOT}/voice"

echo "🎙️  Menir v10.3 Voice Launcher"
echo ""

# Check MCP server
echo "🔍 Checking MCP server..."
if ! curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "❌ MCP server not running"
    echo "Start with: uvicorn menir10.mcp_app:app --port 8080"
    exit 1
fi
echo "✅ MCP server OK"

# Check OpenAI key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set"
    echo "Set with: export OPENAI_API_KEY=sk-proj-..."
fi

# Launch voice interface
echo ""
echo "🎤 Starting voice interface..."
echo ""

python3 "${VOICE_DIR}/menir_voice.py" "$@"
