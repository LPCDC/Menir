import os
import sys
import json
import logging
import hashlib
import re
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, Request, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from neo4j import GraphDatabase

# Setup Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = DATA_DIR
PROPOSALS_DIR = DATA_DIR / "proposals" / "inbox"
VIEWS_DIR = BASE_DIR / "views"

# Append menir_core to path if needed (though usually handled by venv)
sys.path.append(str(BASE_DIR))

# Ensure Directories
PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
VIEWS_DIR.mkdir(parents=True, exist_ok=True)

# Logger Setup (Separate from uvicorn to ensure canonical jsonl format)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("menir_server")

def append_operation_log(data: Dict[str, Any]):
    """Append a structured log entry to data/operations.jsonl."""
    log_file = LOGS_DIR / "operations.jsonl"
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")


# ==========================================
# Security & Config
# ==========================================

security = HTTPBearer()

# Neo4j Config
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://menir-db:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PWD = os.getenv("NEO4J_PWD", "menir123")

driver = None

def get_driver():
    global driver
    if not driver:
        try:
            driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PWD))
            driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {NEO4J_URI}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    return driver


def get_api_token():
    token = os.getenv("MENIR_API_TOKEN")
    if not token and os.getenv("MENIR_MODE") == "prod":
         # In PROD, fail start if no token or weak token (naive check)
         logger.critical("MENIR_MODE is prod but MENIR_API_TOKEN is missing!")
         sys.exit(1)
    return token

API_TOKEN = get_api_token()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify Bearer Token."""
    if not API_TOKEN:
        # If in DEV and no token set, warn but maybe allow? 
        # Plan says: "Recuse tokens fracos" / "Token Bearer obrigatório"
        # Let's enforce it strictly to be safe.
        raise HTTPException(status_code=500, detail="Server misconfiguration: API Token not set.")
    
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return credentials.credentials

# ==========================================
# Models
# ==========================================

class HealthResponse(BaseModel):
    status: str
    components: Dict[str, str]
    version: str

class CypherQuery(BaseModel):
    query: str
    params: Dict[str, Any] = {}

class ViewParams(BaseModel):
    view_id: str
    params: Dict[str, Any] = {}

class SearchQuery(BaseModel):
    project_id: str
    query: str
    top_k: int = 3

class SourceChannel(str, Enum):
    opal_app = "opal_app"
    cli = "cli"
    test_suite = "test_suite"

class SourceMetadata(BaseModel):
    channel: SourceChannel
    app_id: Optional[str] = None

class ProposalInput(BaseModel):
    project_id: str
    type: str
    payload: Dict[str, Any]
    source_metadata: SourceMetadata

# ==========================================
# Logic Helpers
# ==========================================

def validate_readonly_cypher(query: str):
    """Raise error if query contains write keywords."""
    forbidden = ["CREATE", "MERGE", "DELETE", "SET", "REMOVE", "DROP", "DETACH"]
    upper_q = query.upper()
    for word in forbidden:
        # Regex to match whole word boundaries to avoid false positives (e.g. ASSET)
        if re.search(r'\b' + word + r'\b', upper_q):
            raise HTTPException(status_code=400, detail=f"Write operations are forbidden: {word}")

def mask_sensitive_payload(payload: Dict[str, Any]) -> str:
    """Mask large payload for logs."""
    s = json.dumps(payload)
    if len(s) > 100:
        h = hashlib.md5(s.encode()).hexdigest()
        return f"<hash:{h} size:{len(s)}>"
    return s

def execute_cypher(query: str, params: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    """Execute Cypher query and return list of dicts."""
    d = get_driver()
    try:
        with d.session() as session:
            result = session.run(query, params)
            return [record.data() for record in result]
    except Exception as e:
        logger.error(f"Cypher execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database execution error: {str(e)}")


def load_view_query(view_id: str) -> str:
    """Load query from views/{view_id}.cypher"""
    # Sanitize view_id
    safe_id = re.sub(r'[^a-z0-9_]', '', view_id)
    view_path = VIEWS_DIR / f"{safe_id}.cypher"
    if not view_path.exists():
        raise HTTPException(status_code=404, detail=f"View {safe_id} not found")
    return view_path.read_text(encoding="utf-8")

# ==========================================
# FastAPI App
# ==========================================

app = FastAPI(title="Menir Server", version="1.2.0")

@app.on_event("startup")
def startup_event():
    get_driver()

@app.on_event("shutdown")
def shutdown_event():
    global driver
    if driver:
        driver.close()


@app.middleware("http")
async def audit_logger(request: Request, call_next):
    """Audit middleware for operations.jsonl."""
    if request.url.path == "/v1/health":
        return await call_next(request)

    start_ts = datetime.datetime.now().isoformat()
    try:
        response = await call_next(request)
        outcome = "success" if response.status_code < 400 else "error"
        status_code = response.status_code
    except Exception as e:
        outcome = "exception"
        status_code = 500
        raise e
    finally:
        # Log regardless of success/fail
        # We can't easily access request body here without consuming stream, 
        # so detailed payload logging happens in endpoints or requires advanced middleware.
        # For V1, we log the intent here and details in endpoint.
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "action": "api_request",
            "method": request.method,
            "path": request.url.path,
            "outcome": outcome,
            "status": status_code,
            # "user": ... (Identity extracted from token if complex, for now 'bearer')
        }
        append_operation_log(log_entry)
        
    return response

# --- Endpoints ---

@app.get("/v1/health")
def health():
    return {
        "status": "online",
        "components": {
            "neo4j": "connected", # Placeholder checks
            "vector_store": "ready"
        },
        "version": "1.2.0"
    }

@app.get("/v1/meta/state", dependencies=[Depends(verify_token)])
def meta_state():
    # Read session from file or memory
    # Mocking for V1 structure adherence
    return {"session_id": "active_session_123", "active_project": "livro_debora"}

@app.post("/v1/query/cypher", dependencies=[Depends(verify_token)])
def query_cypher(body: CypherQuery):
    validate_readonly_cypher(body.query)
    
    # Execution Logic
    # result = driver.run(...)
    # For now, return safety ack
    return {"result": "would_execute", "query_safe": True}

@app.post("/v1/query/view", dependencies=[Depends(verify_token)])
def query_view(body: ViewParams):
    cypher = load_view_query(body.view_id)
    # Validate just in case file has writes?
    validate_readonly_cypher(cypher)
    
    data = execute_cypher(cypher, body.params)
    return {"view": body.view_id, "data": data}

@app.post("/v1/context/search", dependencies=[Depends(verify_token)])
def context_search(body: SearchQuery):
    if not body.project_id:
        raise HTTPException(status_code=400, detail="project_id is mandatory")
    
    # Search logic...
    return {"results": ["Context result 1", "Context result 2"], "project": body.project_id}

@app.post("/v1/scribe/proposal", dependencies=[Depends(verify_token)])
def create_proposal(body: ProposalInput):
    # Generate ID and TS
    ts_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pid = hashlib.sha256(f"{ts_str}_{body.payload}".encode()).hexdigest()[:8]
    filename = f"PROPOSAL_{ts_str}_{pid}.jsonl"
    
    filepath = PROPOSALS_DIR / filename
    
    proposal_data = {
        "proposal_id": pid,
        "timestamp": datetime.datetime.now().isoformat(),
        "project_id": body.project_id,
        "type": body.type,
        "status": "pending",
        "payload": body.payload,
        "source": body.source_metadata.dict()
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json.dumps(proposal_data))
        
    # Canonical Log (LGPD safe)
    safe_log = {
        "timestamp": datetime.datetime.now().isoformat(),
        "action": "scribe_proposal_created",
        "proposal_id": pid,
        "project_id": body.project_id,
        "payload_mask": mask_sensitive_payload(body.payload)
    }
    append_operation_log(safe_log)
    
    return {"status": "received", "proposal_id": pid}

@app.get("/v1/scribe/proposals/{proposal_id}", dependencies=[Depends(verify_token)])
def get_proposal_status(proposal_id: str):
    # Naive search in dir
    # Real impl might index this or check a Manifest
    for f in PROPOSALS_DIR.glob("*.jsonl"):
        if proposal_id in f.name:
            return {"proposal_id": proposal_id, "status": "pending"} # Mock status logic
    raise HTTPException(status_code=404, detail="Proposal not found")

if __name__ == "__main__":
    import uvicorn
    # Default config, usually run via CLI
    uvicorn.run(app, host="0.0.0.0", port=8000)
