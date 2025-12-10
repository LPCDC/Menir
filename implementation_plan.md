# Phase 1 Hardening Refinement Plan

## 1. `scripts/mcp_server.py` Refactoring

**Gap**: Uses `print()`, duplicate logic, no structured logging for security events (RNF-2).
**Fix**:
- **Logging**: Configure `logging` to use `menir_core` style (JSONL-friendly).
  - Format: `{"ts": "...", "action": "mcp_event", "level": "INFO|WARN|ERROR", ...}`
- **Health Endpoint**: Add `GET /health` returning:
  ```json
  {
    "status": "online",
    "mode": "PROD"|"LAB",
    "auth_secured": boolean,
    "version": "v1.1.1"
  }
  ```
- **Auth Filtering**: Warning logs for 401s must include details (IP/Timestamp).

## 2. `scripts/backup_routine.py` Refactoring

**Gap**: Logs to console/stderr via `logging` but doesn't write to the canonical `logs/operations.jsonl` (RNF-2 integration).
**Fix**:
- Add `append_log(entry)` helper (mirroring `boot_now.py` pattern).
- Write `{"action": "backup", "status": "success", "file": "..."}` to `logs/operations.jsonl`.
- Ensure failure cases log `{"action": "backup", "status": "failure", "error": "..."}`.

## 3. DoD Verification
- [ ] Backup creates file AND logs to `operations.jsonl`.
- [ ] Server log shows "Startup in PROD mode".
- [ ] `/health` confirms security state.
- [ ] Failed auth attempts appear in `operations.jsonl` (or stderr structured log).
