import logging
import os
from fastapi import FastAPI, Body, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# STUBS FOR DATA MODULES
try:
    from menir10.menir10_insights import get_logs, summarize_project, render_project_context
    from menir10.menir10_log import append_log, make_entry
    logging.info("✅ Successfully imported menir10 data modules")
except ImportError as e:
    logging.warning(f"⚠️  Failed to import menir10 modules: {e}")
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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None}
    )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Menir MCP JSON-RPC",
        "version": "10.3"
    }

@app.get("/info")
async def server_info():
    return {
        "server": "Menir Orchestrator",
        "methods": [
            "ping", 
            "boot_now", 
            "list_projects", 
            "project_summary", 
            "search_interactions", 
            "context"
        ]
    }

@app.post("/jsonrpc")
async def jsonrpc_handler(payload: dict = Body(...)):
    # Validate payload is a dict? FastAPI ensures it via signature, 
    # but for [] it calls exception handler (Validation Error).
    # So valid dict logic proceeds here.
    
    # Check JSON-RPC version
    if payload.get("jsonrpc") != "2.0":
         return JSONResponse(
            status_code=400,
            content={"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request: missing jsonrpc"}, "id": payload.get("id")}
         )

    method = payload.get("method")
    msg_id = payload.get("id")
    
    if not method:
         # Missing method
         return JSONResponse(
             status_code=400, # Or 404/200 depend on spec, test says test_invalid_method uses 404, but missing method field is malformed request
             content={"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request: missing method"}, "id": msg_id}
         )
         # Wait, test_invalid_method sends "method": "nonexistent" -> expects 404.
         # test_missing_jsonrpc_version -> expects 400.

    # ... routing ...
    
    if method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"status": "Menir-10 contextual proxy alive", "service": "menir-orchestrator-v10.4.1", "version": "10.3"}
        }

    if method == "boot_now":
        from datetime import datetime
        logs = get_logs()
        total_interactions = len(logs)
        projects_count = len(set(l.get("project_id") for l in logs))
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "repo_root": os.getcwd(),
                "projects_count": projects_count,
                "interactions_count": total_interactions,
                "notes": ["Menir system active"]
            }
        }

    if method == "list_projects":
        params = payload.get("params", {})
        top_n = params.get("top_n", 10)
        logs = get_logs()
        
        from collections import Counter
        project_ids = [entry.get("project_id", "unknown") for entry in logs]
        counter = Counter(project_ids)
        top = counter.most_common(top_n)
        
        projects_list = [{"id": p, "count": c} for p, c in top]
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "projects": projects_list,
                "total_projects": len(counter)
            }
        }

    if method == "project_summary":
        params = payload.get("params", {})
        project_id = params.get("project_id")
        if not project_id:
            # Test expects 200, 400 or 404
            return {"jsonrpc": "2.0", "error": {"code": -32602, "message": "Missing project_id"}, "id": msg_id}
            
        logs = get_logs()
        summary = summarize_project(project_id, logs)
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "project_id": project_id,
                "interaction_count": summary.get("total_count", 0),
                "summary": summary
            }
        }

    if method == "search_interactions":
        params = payload.get("params", {})
        project_id = params.get("project_id")
        intent = params.get("intent_profile")
        limit = params.get("limit", 10)
        
        logs = get_logs()
        results = []
        for entry in logs:
            if project_id and entry.get("project_id") != project_id:
                continue
            if intent and entry.get("intent_profile") != intent:
                continue
            results.append(entry)
            
        results = results[-limit:] 
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "results": results,
                "result_count": len(results)
            }
        }
    
    if method == "context":
        query = payload.get("params", {})
        if isinstance(query, dict):
             target_query = query.get("project_id", "") or query.get("query", "")
             include_markdown = query.get("include_markdown", False)
        else:
             target_query = str(query)
             include_markdown = False

        project_id = next((pid for k, pid in KNOWN_PROJECTS.items() if k in target_query.lower()), None)
        if not project_id and isinstance(query, dict) and "project_id" in query:
             project_id = query["project_id"]

        context_block = ""
        markdown_context = ""
        
        if project_id:
            logging.info(f"🔎 Project match: {project_id}")
            try:
                logs = get_logs()
                logging.info(f"📋 Loaded {len(logs)} total logs")
                summary = summarize_project(project_id, logs, limit=20)
                logging.info(f"📊 Project summary: total={summary.get('total_count')}, sample={summary.get('sample_count')}")
                if summary.get("total_count", 0) > 0:
                    context_block = render_project_context(summary)
                    if include_markdown:
                        markdown_context = f"# Context for {project_id}\n\n{context_block}"
                    logging.info(f"✅ Context rendered ({len(context_block)} chars)")
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
                metadata={"query": str(payload.get("params"))}
            ))
        except:
            pass

        result_data = {
            "project": project_id,
            "project_id": project_id, # Required by test
            "interaction_count": summary.get("total_count", 0) if project_id else 0,
            "recent_interactions": summary.get("interactions", []) if project_id else [],
            "context_layer": f"[CONTEXT LAYER: {project_id or 'GLOBAL'}]\n{context_block}"
        }
        if include_markdown:
            result_data["markdown_context"] = markdown_context

        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": result_data
        }

    return JSONResponse(
        status_code=404,
        content={"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": msg_id}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
