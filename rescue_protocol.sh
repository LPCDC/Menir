#!/bin/bash
set -e

echo "========================================"
echo "🚀 MENIR v10.4.1: RESCUE PROTOCOL (STABLE)"
echo "========================================"

# 0. SYSTEM SETUP
echo "[0/5] 🔧 Checking system tools..."
sudo apt-get update -qq && sudo apt-get install -y jq -qq
echo "      -> System tools ready."

# 1. CLEANUP
echo "[1/5] 🧹 Removing artifacts & orphan processes..."
pkill -f "python menir10/mcp_app.py" || true
rm -f scripts/mcp_server.py menir_allinone.py
mkdir -p menir10
echo "      -> Cleanup complete."

# 2. PYTHON DEPENDENCIES
echo "[2/5] 📦 Installing dependencies..."
pip install fastapi uvicorn requests typer python-dotenv > /dev/null 2>&1
echo "      -> Dependencies installed."

# 3. CREATE THE BRAIN (mcp_app.py)
echo "[3/5] 🧠 Writing menir10/mcp_app.py..."
cat > menir10/mcp_app.py << 'EOF'
import logging
import os
from fastapi import FastAPI, Body, HTTPException

# STUBS FOR DATA MODULES
try:
    from menir10.menir10_insights import get_logs, summarize_project, render_project_context
    from menir10.menir10_log import append_log, make_entry
except ImportError:
    def get_logs(): return []
    def summarize_project(*args, **kwargs): return {"sample_count": 0, "total_count": 0}
    def render_project_context(*args): return "Mock context (Data modules not found)"
    def append_log(*args): pass
    def make_entry(*args, **kwargs): return {}

app = FastAPI(title="Menir v10.4.1 - GraphRAG Orchestrator")
logging.basicConfig(level=logging.INFO)

KNOWN_PROJECTS = {
    "itau": "BancoItau",
    "tivoli": "tivoli",
    "livro": "livro_debora_cap1",
    "debora": "livro_debora_cap1"
}

@app.post("/jsonrpc")
async def jsonrpc_handler(payload: dict = Body(...)):
    method = payload.get("method")
    msg_id = payload.get("id")
    
    if method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"status": "ok", "service": "menir-orchestrator-v10.4.1"}
        }
    
    if method == "context":
        query = payload.get("params", {}).get("query", "").lower()
        project_id = next((pid for k, pid in KNOWN_PROJECTS.items() if k in query), None)
        
        context_block = ""
        if project_id:
            logging.info(f"🔎 Project match: {project_id}")
            try:
                logs = get_logs()
                summary = summarize_project(project_id, logs, limit=20)
                if summary.get("total_count", 0) > 0:
                    context_block = render_project_context(summary)
                else:
                    context_block = f"Mock context for {project_id} (Logs pending ingestion)"
            except Exception as e:
                logging.error(f"Retrieval error: {e}")
                context_block = f"[SYSTEM ERROR: {str(e)}]"
        else:
            context_block = f"No specific project matched. Available: {list(KNOWN_PROJECTS.keys())}"

        try:
            append_log(make_entry(
                project_id=project_id or "general",
                intent_profile="mcp_query",
                flags={"rag_active": True},
                metadata={"query": query}
            ))
        except:
            pass

        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "project": project_id,
                "context_layer": f"[CONTEXT LAYER: {project_id or 'GLOBAL'}]\n{context_block}"
            }
        }

    return {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": msg_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
EOF

# 4. CREATE THE CLI (memoetic_cli.py) - FIXED STUBS
echo "[4/5] ✋ Writing menir10/memoetic_cli.py..."
cat > menir10/memoetic_cli.py << 'EOF'
import argparse
import sys

# CORRECTION: Define stubs instead of exiting, ensuring CLI always runs
try:
    from menir10.menir10_insights import get_logs, summarize_project, render_project_context
except ImportError:
    print("⚠️  Running in stub mode (menir10_insights not found)")
    def get_logs(): return []
    def summarize_project(*args, **kwargs): return {"sample_count": 0}
    def render_project_context(*args): return ""

def main():
    parser = argparse.ArgumentParser(description="Menir Memoetic CLI")
    parser.add_argument("--project", required=True)
    parser.add_argument("--mode", default="summary")
    args = parser.parse_args()
    
    logs = get_logs()
    summary = summarize_project(args.project, logs, limit=50)
    
    print(f"--- 📝 Summary: {args.project} ---")
    if summary.get("sample_count", 0) > 0:
        print(render_project_context(summary))
    else:
        print(f"No logs found for {args.project}. Ready for ingestion.")

if __name__ == "__main__":
    main()
EOF

# 5. INTEGRATION TEST (With Retry Logic)
echo "[5/5] 🔥 Starting End-to-End Test..."

# Start server
nohup python menir10/mcp_app.py > mcp.log 2>&1 &
MCP_PID=$!

# Robust Wait Loop
echo "      Waiting for server (max 15s)..."
MAX_RETRIES=5
COUNT=0
SUCCESS=0

while [ $COUNT -lt $MAX_RETRIES ]; do
    sleep 3
    # Check if port 8080 is answering
    if curl -s http://localhost:8080/docs > /dev/null; then
        SUCCESS=1
        break
    fi
    echo "      ... still waiting ($COUNT)"
    COUNT=$((COUNT+1))
done

if [ $SUCCESS -eq 0 ]; then
    echo "❌ SERVER BOOT FAILED. Log:"
    cat mcp.log
    kill $MCP_PID 2>/dev/null
    exit 1
fi

echo "      📡 Sending JSON-RPC probe..."
RESPONSE=$(curl -s -X POST http://localhost:8080/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"context","id":1,"params":{"query":"status livro debora"}}')

# Validate with jq
if echo "$RESPONSE" | jq -e '.result.project == "livro_debora_cap1"' > /dev/null; then
    echo "✅ SUCCESS: Orchestrator detected project & context."
    echo "   Context Preview:"
    echo "$RESPONSE" | jq '.result.context_layer'
else
    echo "❌ FAILURE: Logic error in response."
    echo "   Raw Response: $RESPONSE"
    cat mcp.log
fi

# Cleanup
kill $MCP_PID 2>/dev/null
echo "========================================"
