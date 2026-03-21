
import os
import logging
import json
import time
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from neo4j import GraphDatabase

# --- Configuration ---
VERSION = "v4.1.0-bridge"
API_TOKEN = os.getenv("MENIR_API_TOKEN", "opal_pilot_token_2025")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://menir-db:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PWD = os.getenv("NEO4J_PWD", "menir123")
PROPOSALS_DIR = Path("data/proposals/inbox") # Governance Queue

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("menir_server")

# --- Lifespan ---
from contextlib import asynccontextmanager
import tempfile

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Sweep orphaned ASGI cross-process locks upon container/uvicorn restart
    lock_dir = Path(tempfile.gettempdir()) / "menir_tenant_locks"
    if lock_dir.exists():
        now = time.time()
        for f in lock_dir.glob("*.lock"):
            try:
                if now - f.stat().st_mtime > 60:
                    f.unlink()
                    logger.info(f"🧹 Lifespan Sweep: Orfan lock {f.name} expurgado (>60s de idade).")
            except OSError:
                pass
    yield

# --- FastAPI App ---
app = FastAPI(title="Menir Bridge", version=VERSION, lifespan=lifespan)
security = HTTPBearer()

# --- Security ---
def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid Authentication Token")
    return credentials.credentials

# --- Models ---
class ProposalInput(BaseModel):
    project_id: str
    type: str # 'create_node', 'ingest_file', etc.
    payload: Dict[str, Any]

class ViewInput(BaseModel):
    view_id: str
    params: Dict[str, Any]

# --- Database Helper ---
def run_cypher(query: str, params: dict = {}):
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PWD))
        driver.verify_connectivity()
        with driver.session() as session:
            result = session.run(query, params)
            data = [record.data() for record in result]
        driver.close()
        return data
    except Exception as e:
        logger.error(f"DB Error: {e}")
        # In Bridge v4.1, we return empty list on error for resilience, but log critical
        return []

# --- Endpoints ---

@app.get("/v1/health")
def health_check():
    """System Vital Signs."""
    db_status = "unknown"
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PWD))
        driver.verify_connectivity()
        db_status = "connected"
        driver.close()
    except Exception as e:
        db_status = f"disconnected ({str(e)})"
    
    return {
        "status": "online",
        "version": VERSION,
        "components": {
            "neo4j": db_status,
            "scribe_queue": "ready" if PROPOSALS_DIR.exists() else "not_found"
        }
    }

@app.post("/v1/scribe/proposal")
async def submit_proposal(proposal: ProposalInput, token: str = Depends(verify_token)):
    """
    The Scribe Ingestion Endpoint.
    Does NOT write to DB directly. Writes a JSONL proposal to the Queue.
    """
    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate ID
    import uuid
    prop_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"PROPOSAL_{timestamp}_{prop_id}.jsonl"
    filepath = PROPOSALS_DIR / filename
    
    # Construct Full Proposal
    data = proposal.dict()
    data["proposal_id"] = prop_id
    data["status"] = "pending"
    data["submitted_at"] = datetime.now().isoformat()
    
    # Write to Disk
    try:
        with open(filepath, "w", encoding='utf-8') as f:
            f.write(json.dumps(data) + "\n")
        logger.info(f"Proposal {prop_id} saved to {filepath}")
        return {"status": "received", "proposal_id": prop_id, "queue_position": "next"}
    except Exception as e:
        logger.error(f"Failed to save proposal: {e}")
        raise HTTPException(status_code=500, detail="Proposal Storage Failed")

@app.post("/v1/query/view")
def execute_view(view_input: ViewInput, token: str = Depends(verify_token)):
    """
    Executes a Named View (Stored Procedure equivalent).
    """
    view_path = Path("views") / f"{view_input.view_id}.cypher"
    
    if not view_path.exists():
        raise HTTPException(status_code=404, detail=f"View '{view_input.view_id}' not found.")
    
    try:
        with open(view_path, "r") as f:
            cypher_query = f.read()
            
        data = run_cypher(cypher_query, view_input.params)
        return {"view": view_input.view_id, "data": data}
        
    except Exception as e:
        logger.error(f"View Execution Error: {e}")
        raise HTTPException(status_code=500, detail="View Execution Failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
