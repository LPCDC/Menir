# Research Notes: Menir API & Opal Integration (v1)

## 1. Headless RAG API Patterns
**Objective**: Confirm standard endpoints for a Headless Graph/RAG system.
**Findings**:
- Standard structure involves separating "Meta/Health", "Ingest/Write" (often async), and "Query/Read" (RAG).
- **Sources**:
    - [Hygraph: Headless CMS patterns](https://hygraph.com) - Emphasizes separation of Content vs. View.
    - [LlamaIndex Patterns](https://llamaindex.ai) - Shows `/query` and `/chat` endpoints as standard.
    - [FastAPI + Neo4j Templates](https://github.com/neo4j-examples) - Standardizes `/graph` and `/vector` routes.

**Decision**: The proposed `v1/query/cypher`, `v1/context/search`, and `v1/scribe/proposals` structure adheres to these best practices.

## 2. Security & Auth
**Objective**: "Simple and Safer" Auth for FastAPI.
**Findings**:
- **OAuth2PasswordBearer** is the "FastAPI standard" but requires a login flow.
- **HTTPBearer** with valid static token is the recognized pattern for machine-to-machine or single-user tools where strict OAuth flows are overkill.
- **Sources**:
    - [FastAPI Security Docs](https://fastapi.tiangolo.com/tutorial/security/)
    - [OWASP REST Security](https://cheatsheetseries.owasp.org/) - Recommends HTTPS + High Entropy Tokens.

**Decision**: Use `HTTPBearer` checking `os.getenv("MENIR_API_TOKEN")`. Simple, verifiable, rotation-friendly (change env var).

## 3. Google Opal Integration
**Objective**: Confirm Opal capabilities for external API consumption.
**Findings**:
- Opal is primarily "No-Code / Visual". It excels at generating UIs but has limited *native, direct* HTTP Client blocks exposed to the end-user without "code" steps.
- **Constraint**: Direct `fetch()` from Opal generated apps isn't always straightforward in the "Mini-App" builder unless using specific extensions or Code Blocks.
- **Mitigation/Design Adjustment**:
    - We will build a **Standard REST API**.
    - If Opal apps cannot call it directly, we will use an orchestration layer (e.g., n8n, Zapier, or a simple "Proxy Script") as the bridge, OR assume the user has access to Opal's "Advanced Code" features.
    - The API design remains robust regardless of the caller (Opal, Postman, or a python script).
- **Sources**:
    - [Google Labs Opal FAQ](https://labs.google/)
    - User's Provided Context (implies capability exists or is desired).

**Conclusion**: Proceed with FastAPI implementation.
