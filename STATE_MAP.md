# Menir v10.4 – Ultra-Short State Map

## 3 Foundational Layers

### 1. Foundation (v10.0–10.2)
**Event Sourcing Core**
- JSONL log format: `menir10_interactions.jsonl`
- Each interaction: `{timestamp, method, project_id, payload}`
- Export pipeline → Neo4j graph
- Per-project insights & analytics
- Boot hooks & state management

**Key Files:**
- `menir10/menir10_log.py` – Logging engine
- `menir10/menir10_export.py` – Cypher generation
- `menir10/menir10_insights.py` – Analytics

---

### 2. Operational Layer (v10.3)
**MCP Server + CLI Integration**
- MCP (Model Context Protocol) on FastAPI
- JSON-RPC endpoint: `http://localhost:8080/jsonrpc`
- CLI: `ask_menir.py` (GPT integration via OPENAI_API_KEY)
- Voice layer: Speech synthesis & recognition hooks
- Deploy script: `all_in_one_setup.sh`
- Test coverage: **21 MCP tests** ✅

**Key Files:**
- `menir10/mcp_app.py` – FastAPI + JSON-RPC server
- `scripts/mcp_server.py` – Standalone runner
- `ask_menir.py` – CLI interface
- `menir10/menir10_boot.py` – Boot sequence

---

### 3. Memoetic Layer (v10.4) ⭐
**Narrative Pattern Extraction**
- `memoetic.py`: Deterministic text analysis (NO LLM)
  - `extract_memoetics()` – Profile generation
  - `summarize_voice()` – Human narrative synthesis
  - `list_memes()` – Recurring themes/terms
- `memoetic_cli.py`: 3-mode CLI
  - `--mode summary` – Top terms + quotes
  - `--mode voice` – Narrative about project
  - `--mode memes` – Recurring patterns
- Test coverage: **41 tests total**, **76% coverage** ✅

**Key Files:**
- `menir10/memoetic.py` (292 lines)
- `menir10/memoetic_cli.py` (45 lines)
- `tests/test_memoetic.py` (76 lines)

---

## Release Package Contents

**File:** `Menir_v10.4-custom_full.tar.gz` (104 KB)

✅ Source code (menir10/ + tests/)  
✅ Documentation (QUICKSTART.md, MEMOETIC_GUIDE.md, RELEASE_NOTES_v10.4.md, **HOW_TO.md**)  
✅ Test suite (41/41 passing, 76% coverage)  
✅ Smoke test script (menir_final_smoketest.sh)  
✅ Coverage HTML report (coverage_report/)  
✅ Git history & tags (v10.4 tag created)

---

## State Validation Checklist

Run this to confirm everything works:

```bash
# 1. Unpack & setup
tar -xzf Menir_v10.4-custom_full.tar.gz
cd Menir
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Run tests
pytest -q  # → 41 passed ✅

# 3. Start MCP server
uvicorn menir10.mcp_app:app --host 0.0.0.0 --port 8080 &

# 4. Test boot_now
curl -X POST http://localhost:8080/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"boot_now","id":1}' | jq .

# 5. Test memoetic CLI
python -m menir10.memoetic_cli --project personal --mode voice

# 6. Run smoke test
./menir_final_smoketest.sh  # → All 6 checks pass ✅
```

---

## Next Steps After Release

### Option A: Continue in This Codespace
```bash
# You have everything ready:
source .venv/bin/activate
pytest -q          # 41 tests
uvicorn ...        # MCP server
python -m menir10.memoetic_cli ...  # CLI tools
```

### Option B: Fresh Start (Recommended for Deployment)
1. **Close this Codespace**
2. **Download the release package** to your local machine or deployment server
3. **Follow the setup steps** in HOW_TO.md or QUICKSTART.md
4. **Open a new chat** and type `BOOT NOW` to continue development

---

## Git History Summary

```
d290a86 docs: add quick how-to guide for v10.4 installation and usage
6f2c1a5 docs: add comprehensive release notes for v10.4
a3f8b9c ci: add final smoke test validation script
2e5d7f1 feat(memoetic-cli): Add CLI interface for memoetic analysis
5a1b4c2 feat(memoetic): Add narrative pattern extraction layer
```

Tags:
- `v10.4` – Current production release
- `v10.3` – Previous operational release
- `v10.0` – Foundation release

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Total Tests | 41 |
| Tests Passing | 41 (100%) |
| Code Coverage | 76% |
| Lines Analyzed | 1016 |
| Release Package Size | 104 KB |
| Included Files | 115+ |
| Python Version | 3.12.1 |
| FastAPI Version | 0.123.9 |
| pytest Version | 9.0.1 |

---

## Ready to Deploy? ✅

**Current Status:** Production ready

- ✅ All tests passing
- ✅ Coverage validated
- ✅ MCP server operational
- ✅ CLI tools functional
- ✅ Documentation complete
- ✅ Release package created
- ✅ Smoke test validated

**Next action:** Close this Codespace, deploy the package, or open a new chat with `BOOT NOW`.

---

## v10.4.1 – Audit Cleanup

**Legacy Files Archived:**
- `scripts/mcp_server.py` → `legacy/mcp_server_legacy.py` (old Flask-based MCP server)
- `menir_allinone.py` → `legacy/menir_allinone_legacy.py` (experimental all-in-one CLI)
- `scriptsmcp_server.py` → `legacy/mcp_server_stray.py` (stray duplicate)

**Official Entrypoints (v10.4+):**
- **MCP Server:** `uvicorn menir10.mcp_app:app --host 0.0.0.0 --port 8080`
- **Memoetic CLI:** `python -m menir10.memoetic_cli --project <name> --mode [summary|voice|memes]`
- **Boot Script:** `python scripts/boot_now.py`
- **GPT CLI:** `python ask_menir.py "<query>"` (requires OPENAI_API_KEY)

**Rationale:**
- Consolidates MCP implementation into single, tested `menir10/mcp_app.py`
- Removes redundant or outdated CLI wrappers
- Improves maintainability and reduces confusion about which entrypoints are current
- All legacy code preserved in `./legacy/` for reference if needed
