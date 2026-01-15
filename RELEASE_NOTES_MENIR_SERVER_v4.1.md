# Release Notes - Menir Bridge v4.1

**Date**: 2026-01-14
**Status**: Production Ready

## 🛠️ Technical Stack Update
- **The Engine**: Upgraded `MenirExtractor` to prioritize **Gemini 2.0 Flash** (Experimental) with robust fallback to `1.5 Flash`.
- **The Bridge**: Restored `menir_server.py` to full Governance API (`/v1/*`), replacing the detected prototype.
- **The Logic**: Enforced Root-based Hierarchical Constraints in Neo4j:
    - `User.name` IS UNIQUE
    - `Project.name` IS UNIQUE
    - `Document.original_path` IS UNIQUE

## 📈 Functional Status
- **Health**: `/v1/health` verified online (`v4.1.0-bridge`).
- **Pipeline**: Watcher -> Scribe -> Graph verified with "Silent Archivist" test data.
- **Intelligence**: Multi-provider support (Gemini/OpenAI) with versioning logic.

## 🚀 Deployment Instructions
1. `docker compose down`
2. `docker compose up -d`
3. Ensure `.env` contains valid `GEMINI_API_KEY`.
