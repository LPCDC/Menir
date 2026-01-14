# MENIR SYSTEM: ENGINEER HANDOVER PACK (v1.2)

**Role:** You are the Lead Engineer for Menir Vital, a Headless Personal OS.
**Architecture:** Python (FastAPI/Scripts) + Neo4j (Graph) + Vector Store + Google Opal (Frontend).

## 1. Core Principles
- **Headless First:** Logic lives in `scripts/menir_server.py`. UIs are ephemeral (Opal).
- **Zero-Trust Write:** Never write to Neo4j directly via API. Generate `Proposals` (JSONL).
- **Applicator Pattern:** Apply proposals via `menir apply --commit`.
- **Canoncial Views:** Use `.cypher` files in `views/` for complex queries.

## 2. Directory Map
- `scripts/menir_cli.py`: Unified entry point (`start`, `server`, `apply`).
- `scripts/menir_server.py`: FastAPI backend.
- `scripts/apply_proposals.py`: Governing writer logic.
- `data/proposals/`: Inbox for JSONL write intents.
- `views/`: Cypher templates.
- `menir_core/`: internal libraries (graph driver, embeddings).

## 3. Current State (v1.2)
- **Status:** Server is stable. Applicator is implemented.
- **Immediate Goal:** Activate Google Opal integrations using the `Tunnel` + `Token` strategy.
- **Active Projects:**
    - "Livro Débora": Needs Scribe loop active (Creator App -> Proposal -> Apply).
    - "Itaú": Needs financial ingestion view.

## 4. How to Engineer
- When asked to feature X:
    1. Check if it fits the "Headless" model.
    2. Implement logic in Python.
    3. create/update a `view` or `scribe` type.
    4. Provide the Opal prompt for the UI.

## 5. Security
- Auth: `HTTPBearer` with `MENIR_API_TOKEN`.
- Logs: LGPD masked in `data/operations.jsonl`.
