# Menir Server API v1: Design & Governance

## 1. Overview
The **Menir Server** transforms the local "Personal OS" into a "Headless Intelligence Engine".
It handles:
- **Read**: Secure, semantic querying of the Neo4j graph and Vector stores.
- **Write**: Governed ingestion via **Proposals** (Scribe). **No direct write access** is allowed via API.
- **Auth**: Simple, high-entropy Bearer Token protection.

## 2. Authentication
- **Mechanism**: `HTTPBearer` (Authorization: Bearer <token>)
- **Token Source**: Server checks `MENIR_API_TOKEN` env var.
- **Security**:
    - **Startup Check**: If `MENIR_MODE=prod` and generic/default token is detected -> Startup fails.
    - HTTPS (via Tunnel/Twin) is mandatory for transport.

## 3. Endpoints Specification

### A. Meta & Health
#### `GET /v1/health`
- **Desc**: System heartbeat. Checks Neo4j connection and MCP status.
- **Response**:
```json
{
  "status": "online",
  "components": {
    "neo4j": "connected",
    "vector_store": "ready"
  },
  "version": "1.1.1"
}
```

#### `GET /v1/meta/state`
- **Desc**: Returns current session ID and active project context.
- **Response**: `{"session_id": "...", "active_project": "livro_debora"}`

### B. Query (Read-Only)
#### `POST /v1/query/cypher`
- **Desc**: Raw Cypher execution (Read-Only Mode enforced strictly).
- **Security**: Regex filter blocks `CREATE|MERGE|DELETE|SET|REMOVE|DROP` case-insensitive.
- **Input**:
```json
{
  "query": "MATCH (n:Character) RETURN n LIMIT 5",
  "params": {}
}
```

#### `POST /v1/query/view`
- **Desc**: Execute a **Canonical View** (pre-defined Cypher stored in `views/*.cypher`).
- **Input**:
```json
{
  "view_id": "last_bar_visits",
  "params": { "limit": 5 }
}
```
- **Benefit**: Secure, optimized, and decouples prompt from DB schema.

#### `POST /v1/context/search`
- **Desc**: RAG entry point. Semantic search in vector store.
- **Constraint**: `project_id` is **mandatory**.
- **Input**: 
```json
{
  "project_id": "livro_debora",
  "query": "Quem é o pai da Débora?",
  "top_k": 3
}
```

### C. Scribe (Governance/Write)
#### `POST /v1/scribe/proposals`
- **Desc**: The ONLY way to ingest data. Creates a `Proposal` file to be reviewed.
- **Input**:
```json
{
  "project_id": "livro_debora",
  "type": "narrative_fragment",
  "payload": {
    "text": "...",
    "source_url": "..."
  },
  "source_metadata": {
    "channel": "opal_app", 
    "app_id": "viewer_123"
  }
}
```
*Note: `channel` enum: `opal_app`, `cli`, `test_suite`.*

- **Behavior**:
    1.  Validates payload/ontology.
    2.  Generates a JSONL file in `data/proposals/`.
    3.  Returns Proposal ID.

#### `GET /v1/scribe/proposals/{id}`
- **Desc**: Check status of a proposal (`pending`, `applied`, `rejected`).

## 4. Governance Rules
1.  **Zero-Trust Write**: The API cannot write to the Graph. It produces *Artifacts* (JSONL files).
2.  **Audit Trail**: Every request (except health) is logged to `data/operations.jsonl`.
3.  **Data Minimization (LGPD)**: 
    - **Payload masking**: If payload string > 100 chars, log ONLY the hash and size (e.g., `<hash:ab12... size:1500>`). 
    - No literal sensitive data dumps in logs.

## 5. Directory Structure
- `scripts/menir_server.py`: FastAPI App.
- `views/`: Directory for `.cypher` templates.
- `data/proposals/`: Inbox for generated proposals.
