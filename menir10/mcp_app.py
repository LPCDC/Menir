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
