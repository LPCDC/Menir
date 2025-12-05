"""
FastAPI JSON-RPC endpoint for Menir MCP contextual proxy (v10.3).

Exposes all MCP methods via POST /jsonrpc for remote access.
Suitable for deployment as microservice or local development server.

Usage:
    uvicorn menir10.mcp_app:app --host 0.0.0.0 --port 8080
    
    # Test via curl:
    curl -X POST http://localhost:8080/jsonrpc \
      -H "Content-Type: application/json" \
      -d '{"jsonrpc":"2.0","method":"ping","id":1}'
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import json
from datetime import datetime, timezone
from typing import Any, Dict

from menir10 import mcp_server

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - MCP_APP - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Menir MCP JSON-RPC Server",
    description="Contextual proxy for project management and interaction logging",
    version="10.3",
)

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Menir MCP JSON-RPC",
        "version": "10.3",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/jsonrpc")
async def jsonrpc_endpoint(request: Request):
    """
    JSON-RPC 2.0 endpoint for all MCP methods.
    
    Expected payload:
    {
        "jsonrpc": "2.0",
        "method": "ping|boot_now|context|project_summary|list_projects|search_interactions",
        "params": {...},
        "id": request_id
    }
    """
    try:
        payload = await request.json()
        
        # Validate JSON-RPC 2.0 format
        if not isinstance(payload, dict):
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error: request must be a JSON object",
                    },
                    "id": None,
                },
                status_code=400,
            )
        
        jsonrpc_version = payload.get("jsonrpc")
        method = payload.get("method")
        params = payload.get("params", {})
        req_id = payload.get("id")
        
        # Validate jsonrpc version
        if jsonrpc_version != "2.0":
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32600,
                        "message": "Invalid Request: jsonrpc must be 2.0",
                    },
                    "id": req_id,
                },
                status_code=400,
            )
        
        # Validate method
        if method not in mcp_server.METHODS:
            logger.warning(f"Method not found: {method}")
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}",
                    },
                    "id": req_id,
                },
                status_code=404,
            )
        
        # Call method
        logger.info(f"Calling method={method}, params_count={len(params) if params else 0}")
        handler = mcp_server.METHODS[method]
        result = handler(params if params else None)
        
        # Log success
        logger.info(f"Method {method} succeeded")
        
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result,
            }
        )
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}",
                },
                "id": None,
            },
            status_code=400,
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error processing JSON-RPC request: {e}")
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}",
                },
                "id": payload.get("id") if isinstance(payload, dict) else None,
            },
            status_code=500,
        )


@app.get("/info")
async def server_info():
    """Get server and MCP information."""
    return {
        "server": {
            "name": "Menir MCP JSON-RPC",
            "version": "10.3",
            "endpoint": "/jsonrpc",
        },
        "methods": list(mcp_server.METHODS.keys()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    logger.info("🚀 Starting Menir MCP JSON-RPC Server at http://0.0.0.0:8080")
    logger.info("📚 OpenAPI docs available at http://localhost:8080/docs")
    logger.info("❤️ Health check: http://localhost:8080/health")
    uvicorn.run(
        "menir10.mcp_app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
    )
