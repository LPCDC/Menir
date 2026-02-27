# Release Notes - Menir V3.0 "Honest Mode"

**Release Date:** 2026-01-18
**Codename:** Honest Mode

## Features
- **Hard-Stop Audit**: Ingestion strictly halts if audit (Google Sheets) fails.
- **Neo4j Driver v5**: Updated transaction syntax (`execute_write`) for modern drivers.
- **Gemini Flash Free Tier**: Optimized for `gemini-flash-latest` to run cost-free.
- **Cloud Archive Isolation**: Implemented `menir_drive.py` which moves files on Drive to prevent re-download loops.
- **Scope Isolation**: Strict project and SHA-256 constraints enforced on the graph.
