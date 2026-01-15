# Release Notes: Menir Server v1 (2025-12-12)

## 🚀 Released Features
- **Menir Server Core**: FastAPI implementation running on `scripts/menir_server.py`.
- **Governed API**:
    - **Read-Only**: `/v1/query/cypher` strictly blocks write operations.
    - **Write-via-Proposal**: `/v1/scribe/proposals` is the single channel for ingestion.
- **Security**:
    - `HTTPBearer` authentication required.
    - Startup fails in PROD if token is weak/missing.
- **Observability**:
    - LGPD-compliant Audit Logs (`data/operations.jsonl`) showing hashes instead of massive payloads.

## 📋 Canonicity Updates
- **Views**: `/v1/query/view` endpoint decouples SQL/Cypher from the Client.
- **Proposals**: New standard JSONL format for intermediate data artifacts.

## ⚠️ Known Limitations
1.  **Opal Integration**: Direct calls from Google Opal may require an intermediate Bridge (n8n/Cloud Function) depending on the specific Opal plan/capability available to the user.
2.  **Mocked DB**: For this release, the Mock DB response is active in some endpoints until the Neo4j Driver is fully injected from `menir_core`.

## 🔮 Next Steps
1.  **Implement Opal Bridge**: Set up the n8n or Proxy layer if Direct API fails in testing.
2.  **Scribe Applicator**: Build the CLI tool to process the `pending` proposals in `data/proposals/`.
