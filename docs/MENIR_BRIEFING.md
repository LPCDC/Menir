# MENIR – Comprehensive Briefing for Code Assistant (Gemini/Claude)

## Executive Summary

**Menir** is a pseudo-OS and knowledge engineering platform designed to serve as a persistent, auditable foundation for project management, interaction logging, risk inference, and collaborative knowledge building. It bridges on-site code development (GitHub), local state machines (Python modules), and future off-site resilience (Google Drive, Neo4j graph).

**Current Reality (as of 2025-12-05):**
- Menir 10.2 is stable: canonical logging module (`menir10.menir10_log.append_log`), CLI wrappers, and tested workflows.
- **NOT** a monolithic framework; rather, a collection of thin, modular Python packages and shell utilities that cooperate around JSONL-based event logs.
- Fully functional for: boot events, interaction logging per project, daily reports, Cypher export templates.
- **NOT YET** implemented: Neo4j graph backend, live risk oracle, automated memory server, or full GPT integration with mandatory graph queries.

---

## 1. Core Vision & Philosophy

### 1.1 The Problem Menir Solves

Real-world project management involves:
- **Multiple voices** (architects, engineers, clients, syndicates).
- **Scattered context** (emails, calls, PDFs, decisions in heads).
- **No audit trail** at the interaction layer.
- **Risk blindness** (decisions made without historical pattern awareness).
- **Knowledge loss** at person-turnover or project closure.

Menir's goal: **Create a thin, auditable event stream that captures project interactions and makes them queryable, exportable, and analyzable.**

### 1.2 Core Tenets

1. **Event-First**: Everything is an interaction → JSONL entry.
2. **Project-Scoped**: All events carry `project_id` (e.g., `SaintCharles_CM2025`, `itau_15220012`).
3. **Immutable Logs**: Once written, logs are append-only (JSONL).
4. **Composable Export**: Logs → Cypher, Markdown reports, GPT context, future analytics.
5. **Minimal Dependencies**: Core functionality relies on stdlib (json, pathlib, uuid, datetime) + optional pytest/neo4j for extensions.
6. **Resilience**: Off-site backup strategy (Google Drive snapshots, GitHub archives).

---

## 2. Architecture Overview

### 2.1 Layered Structure

```
┌─────────────────────────────────────────────────────────────┐
│ User/CLI Layer (scripts/menir10_*.py)                       │
│  - menir10_boot_cli.py (enforces MENIR_PROJECT_ID)          │
│  - menir10_log_cli.py (append interactions)                 │
│  - menir10_daily_report.py (summarize by project)           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Canonical Module Layer (menir10/*)                          │
│  - menir10_log.py (core: append_log, MissingProjectIdError) │
│  - menir10_export.py (logs → Cypher, project grouping)      │
│  - menir10_insights.py (summarize, render context)          │
│  - menir10_boot.py (boot event sequencing)                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Data Layer (local filesystem)                               │
│  - logs/menir10_interactions.jsonl (append-only event log)  │
│  - menir_state.json (project registry + defaults)           │
│  - exports/menir10_interactions.cypher (for Neo4j import)   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Future: Neo4j Graph + Risk Oracle (NOT YET)                 │
│  - Nodes: Project, Person, Interaction, Decision, Risk      │
│  - Queries: pattern matching, anomaly detection             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Key Modules

| Module | Purpose | Status |
|--------|---------|--------|
| `menir10.menir10_log` | Canonical logger; enforces project_id | ✅ Stable (v10.2) |
| `menir10.menir10_export` | Convert logs → Cypher/JSON; group by project | ✅ Stable |
| `menir10.menir10_insights` | Summarize projects; render context for GPT | ✅ Stable |
| `menir10.menir10_boot` | Boot event sequencing and logging | ✅ Stable |
| `scripts/menir10_log_cli.py` | CLI: register interactions | ✅ Stable |
| `scripts/boot_now.py` | Legacy boot script | ✅ Functional |
| Neo4j integration | Live graph queries, risk detection | ❌ TODO |
| Memory server / FastAPI | HTTP API for remote logging | ❌ TODO |
| GPT integration layer | Mandatory graph context before reply | ❌ TODO |

---

## 3. Current Capabilities (What Works Today)

### 3.1 Interaction Logging

**Command:**
```bash
export MENIR_PROJECT_ID=SaintCharles_CM2025
python scripts/menir10_log_cli.py -c "Reunião com síndico" --intent-profile boot
```

**Result:** JSONL entry appended to `logs/menir10_interactions.jsonl`:
```json
{
  "interaction_id": "uuid-here",
  "project_id": "SaintCharles_CM2025",
  "intent_profile": "boot",
  "created_at": "2025-12-05T12:30:00+00:00",
  "updated_at": "2025-12-05T12:30:00+00:00",
  "flags": {},
  "metadata": {"stage": "single", "status": "ok", "content": "Reunião com síndico"}
}
```

**Features:**
- Enforces `MENIR_PROJECT_ID` (from env or `-p` flag).
- Supports multiple `intent_profile` values: `boot`, `note`, `call`, `summary`, etc.
- Returns `interaction_id` for traceability.

### 3.2 Daily Reports

**Command:**
```bash
python scripts/menir10_daily_report.py --top-n 3 --limit 20
```

**Output:** Markdown report grouping interactions by project, showing top 3 projects, up to 20 interactions each.

### 3.3 Cypher Export

**Command:**
```bash
python menir10_export.py
```

**Output:** `exports/menir10_interactions.cypher` with CREATE statements for importing into Neo4j.

**Example Cypher snippet:**
```cypher
CREATE (:Project {name: 'SaintCharles_CM2025'});
CREATE (:Interaction {id: 'abc123', content: 'Reunião com síndico'});
MATCH (p:Project {name: 'SaintCharles_CM2025'}), (i:Interaction {id: 'abc123'})
CREATE (p)-[:HAS_INTERACTION]->(i);
```

### 3.4 Project Registry

**File:** `menir_state.json`

```json
{
  "projects": {
    "SaintCharles_CM2025": {
      "id": "SaintCharles_CM2025",
      "name": "Edifício Saint Charles – Áreas Comuns",
      "category": "Condominios_Guaruja",
      "status": "ativo",
      "default_env": {"MENIR_PROJECT_ID": "SaintCharles_CM2025"},
      "notes": "CM-2025-ARQ-008 – reforma e requalificação das áreas comuns."
    }
  }
}
```

### 3.5 Testing & CI

- **Unit tests:** `test_menir10_log.py`, `tests/test_menir10_*.py`.
- **CI/CD:** `.github/workflows/menir10-tests.yml` runs `pytest -q` + `python -m unittest discover -v` on push/PR.
- **All tests passing:** ✅ 21 passed (pytest) + 16 passed (unittest).

---

## 4. Current State & Roadmap

### 4.1 What's Implemented (Chapters 1–2)

| Component | Status | Notes |
|-----------|--------|-------|
| Boot event logging | ✅ | `scripts/boot_now.py` + `menir10_boot.py` |
| Interaction JSONL | ✅ | `menir10.menir10_log.append_log` |
| Project scoping | ✅ | `MENIR_PROJECT_ID` env var |
| CLI wrappers | ✅ | `menir10_log_cli.py`, `menir10_boot_cli.py` |
| Export to Cypher | ✅ | `menir10_export.py` |
| Daily reports | ✅ | `menir10_daily_report.py` |
| Tests & CI | ✅ | GitHub Actions + pytest + unittest |
| Documentation | ✅ | `MENIR_INTERNAL.md`, `README_SAINT_CHARLES.md` |

### 4.2 What's Missing (Chapters 3+)

| Component | Priority | Description |
|-----------|----------|-------------|
| **Neo4j Backend** | High | Live graph database; nodes for Project, Person, Decision, Risk. |
| **Risk Oracle** | High | Pattern detection from interaction logs; warn on risky decisions. |
| **Memory Server** | Medium | FastAPI HTTP endpoint for remote logging (multi-user). |
| **GPT Integration** | Medium | Mandatory graph query before LLM response; inject context. |
| **Resilience (Drive)** | Low | Automated snapshot export to Google Drive + off-site backup. |
| **UI/Dashboard** | Low | Web front-end to browse projects, interactions, decisions. |

---

## 5. Real-World Example: Saint Charles Project

**Project:** `SaintCharles_CM2025` (Edifício Saint Charles – Áreas Comuns)

**Parties:**
- Client: Condomínio Edifício Saint Charles
- Architect: Caroline Moreira (SME)
- Visual: LibLabs (Luiz Paulo Carvalho)

**Interaction Log (sample):**
```
2025-11-27: Contrato assinado com Carol (arquitetura).
2025-11-28: Proposta LibLabs assinada (renders).
2025-11-30: Teste via CLI canônico (menir10_log).
2025-12-01: Boot Menir10 para projeto Saint Charles.
```

**Cypher Graph (intended):**
```
(SaintCharles_CM2025:Project)
  ├─[:HAS_PERSON]→ (Caroline Moreira:Person)
  ├─[:HAS_PERSON]→ (Luiz Paulo Carvalho:Person)
  ├─[:HAS_INTERACTION]→ (i001:Interaction {content: "Contrato assinado..."})
  ├─[:HAS_INTERACTION]→ (i002:Interaction {content: "Proposta LibLabs..."})
  └─[:HAS_RISK]→ (r001:Risk {pattern: "scope_creep", severity: "medium"})
```

**Daily Report (Markdown):**
```markdown
# Menir-10 Daily Context

## SaintCharles_CM2025
- Total interactions: 4
- Status: ativo
- Recent: Boot Menir10; projeto está em fase de renderização.

## itau_15220012
- Total interactions: 2
- Status: ativo
- Recent: Ligação com gerente sobre prazo de documentação.
```

---

## 6. Constraints & Assumptions

### 6.1 Constraints

1. **Single-User (for now):** No locking/concurrency; assumes sequential appends to JSONL.
2. **No Encryption at Rest:** JSONL is plain JSON; PII/sensitive data must be excluded upstream.
3. **No Live Graph:** Cypher is generated but not automatically imported; manual Neo4j setup required.
4. **No GPT Feedback Loop:** Logging is one-way; no automatic decision annotation from LLM responses.

### 6.2 Assumptions

1. **Environment Variables:** Projects use `MENIR_PROJECT_ID` set before scripts run.
2. **Filesystem Access:** All processes run on same machine (or NFS-mounted repo).
3. **Git as Canonical:** Code/config changes tracked in GitHub; Menir logs are *additional* artifacts.
4. **Manual Imports:** Users manually run `menir10_export.py` and import Cypher into Neo4j.

---

## 7. Suggested Incremental Features

### Phase 3a: Neo4j Foundation (1–2 weeks)

**Goal:** Make graph queries live and real-time.

**Tasks:**
1. **Auto-Import on Export:** Modify `menir10_export.py` to optionally connect to Neo4j and MERGE nodes/edges.
2. **Constraint Definitions:** Create uniqueness constraints on `Project.id`, `Person.email`, `Interaction.id`.
3. **Relationship Inference:** From metadata (e.g., "person_id": "carol@mail.com"), auto-link Person nodes.
4. **Query Examples:** Provide sample Cypher queries for:
   - Top projects by interaction count.
   - People involved per project.
   - Risk patterns (e.g., interactions with "urgent" tag).

**Deliverables:**
- `menir10/menir10_neo4j.py` (new module for graph operations).
- Updated `menir10_export.py` with `--neo4j-import` flag.
- Integration test connecting to a test Neo4j instance (Docker).

### Phase 3b: Risk Oracle (1–2 weeks)

**Goal:** Detect risky patterns and flag them.

**Tasks:**
1. **Risk Pattern Library:** Define rule-based patterns (e.g., "3+ urgent flags in 1 day → escalation risk").
2. **Scorer Module:** `menir10/menir10_risk.py` with `score_project(project_id)` returning risk level + details.
3. **CLI Command:** `python scripts/menir10_risk_cli.py --project SaintCharles_CM2025` → prints risk report.
4. **Annotations:** Store risk scores back to Neo4j as Risk nodes linked to Projects.

**Deliverables:**
- `menir10/menir10_risk.py` with pattern detection.
- `scripts/menir10_risk_cli.py` CLI.
- Example risk patterns (scope creep, communication gaps, schedule slip).

### Phase 3c: Memory Server (1–2 weeks)

**Goal:** Enable remote logging via HTTP API.

**Tasks:**
1. **FastAPI Skeleton:** Create `scripts/menir10_server.py` with:
   - `POST /api/v1/interact` → logs interaction, returns interaction_id.
   - `GET /api/v1/project/{project_id}/summary` → returns daily context.
   - `GET /api/v1/risk/{project_id}` → returns risk report.
2. **Auth:** Simple bearer token validation (env var `MENIR_API_TOKEN`).
3. **Docker Deployment:** Dockerfile + docker-compose.yml for local dev.
4. **Client SDK:** Simple Python client in `menir10/client.py` for remote logging.

**Deliverables:**
- `scripts/menir10_server.py` (FastAPI app).
- `menir10/client.py` (HTTP client).
- Docker setup for local testing.

### Phase 3d: GPT Integration Layer (2–3 weeks)

**Goal:** Inject project context into GPT queries; enforce graph awareness.

**Tasks:**
1. **Context Injector:** `menir10/menir10_gpt.py` with function:
   ```python
   def enrich_prompt(user_query, project_id) -> str:
       """Prepend project context + recent interactions + risks to user query."""
   ```
2. **Mandatory Lookup:** If project_id in query, auto-fetch 20 recent interactions + top risks.
3. **GPT Function Calling:** Implement structured calls to Neo4j queries from GPT responses.
4. **Integration Example:** Jupyter notebook showing "user asks question → Menir fetches context → GPT replies with citations".

**Deliverables:**
- `menir10/menir10_gpt.py` module.
- Example notebook: `docs/examples/gpt_integration.ipynb`.
- CLI: `scripts/menir10_ask_cli.py --project SaintCharles_CM2025 "What's the status?"`.

### Phase 3e: Resilience & Drive Integration (1 week)

**Goal:** Automated backups to Google Drive.

**Tasks:**
1. **Snapshot Script:** `scripts/menir10_snapshot.sh` that:
   - Creates `git archive` + snapshots logs + state.
   - Computes SHA256 integrity hash.
   - Uploads to Google Drive via `gdown` or `google-auth` library.
2. **Restore Script:** `scripts/menir10_restore.sh` to pull snapshots from Drive and verify checksums.
3. **CI Job:** GitHub Action to auto-snapshot on release tags.
4. **3-2-1 Validation:** Document how local + GitHub + Drive satisfy backup requirements.

**Deliverables:**
- `scripts/menir10_snapshot.sh` + `menir10_restore.sh`.
- GitHub Action workflow for automated snapshots.
- `docs/architecture/menir_drive_strategy.md` (resilience plan).

---

## 8. Success Criteria

By end of Phase 3:

- ✅ **Logging:** 100+ interactions logged across 5+ projects.
- ✅ **Graph:** Live Neo4j queries returning project summaries, people, decisions.
- ✅ **Risk:** Automated risk scoring on 3+ patterns; zero false positives on known benign projects.
- ✅ **API:** Memory server handling 10+ req/sec; latency < 200ms.
- ✅ **GPT:** Integration demo showing context injection + annotated responses.
- ✅ **Resilience:** Snapshots created every 24h; restore time < 5 min.
- ✅ **Tests:** Coverage > 80%; all CI passing on every commit.

---

## 9. Call to Action for Code Assistant

**Questions for Gemini/Claude:**

1. **Architecture Review:**
   - Does the layered design (CLI → Canonical Module → JSONL → Export) sound solid, or would you suggest a different split?
   - Should we invest in an ORM (SQLAlchemy) or keep JSONL + manual parsing?

2. **Neo4j Integration:**
   - How would you handle schema versioning when the graph evolves (new relationships, node properties)?
   - Should we use Cypher constraints or Python-side validation for data integrity?

3. **Risk Patterns:**
   - Beyond scope creep, communication gaps, and schedule slip, what other red flags should a construction/project management system detect?
   - Would a Bayesian or ML-based approach be better than rule-based patterns?

4. **GPT Integration:**
   - How should we handle prompt injection if users can craft interaction content freely?
   - Should we version the "context injection" format so LLM responses remain stable across Menir updates?

5. **Performance & Scale:**
   - At what log size does JSONL append become a bottleneck? (millions of rows?)
   - Should we partition logs by project or by time window?

6. **Testing & Quality:**
   - What integration tests would you add beyond the current unit tests (JSONL validity, Cypher correctness, Neo4j import)?
   - Should we add property-based testing (Hypothesis) for risk detection?

7. **User Experience:**
   - Would a TUI (terminal UI) for browsing projects be more useful than shell scripts + markdown reports?
   - Should daily context auto-email team members, or pull-based only?

**Open Suggestions:** Please share any observations on architectural debt, performance concerns, or feature gaps you foresee.

---

## 10. Repository Structure Reference

```
LPCDC/Menir/
├── menir10/                          # Canonical package
│   ├── __init__.py
│   ├── menir10_log.py                # ✅ append_log (core)
│   ├── menir10_export.py             # ✅ Cypher generation
│   ├── menir10_insights.py           # ✅ Summarization
│   ├── menir10_boot.py               # ✅ Boot events
│   └── menir10_risk.py               # ❌ TODO (Phase 3b)
│
├── scripts/
│   ├── boot_now.py                   # ✅ Legacy boot
│   ├── menir10_boot_cli.py           # ✅ Boot with PROJECT_ID enforcement
│   ├── menir10_log_cli.py            # ✅ Log CLI
│   ├── menir10_daily_report.py       # ✅ Daily context
│   ├── menir10_server.py             # ❌ TODO (Phase 3c)
│   ├── menir10_ask_cli.py            # ❌ TODO (Phase 3d)
│   ├── menir10_snapshot.sh           # ❌ TODO (Phase 3e)
│   └── menir10_restore.sh            # ❌ TODO (Phase 3e)
│
├── logs/
│   ├── menir10_interactions.jsonl    # ✅ Main event log
│   └── operations.jsonl              # ✅ Boot log
│
├── exports/
│   └── menir10_interactions.cypher   # ✅ Generated Cypher
│
├── tests/
│   ├── test_menir10_*.py             # ✅ Unit tests
│   └── test_integration_*.py         # ❌ TODO
│
├── projects/
│   ├── SaintCharles/
│   │   └── README_SAINT_CHARLES.md   # ✅ Project doc
│   └── ...
│
├── docs/
│   ├── architecture/
│   │   └── menir_drive_strategy.md   # 🚧 WIP (Phase 3e)
│   └── examples/
│       └── gpt_integration.ipynb      # ❌ TODO (Phase 3d)
│
├── menir_state.json                  # ✅ Project registry
├── MENIR_INTERNAL.md                 # ✅ Quick reference
├── .github/workflows/
│   └── menir10-tests.yml             # ✅ CI/CD
│
└── requirements.txt                  # ✅ Dependencies
```

---

## 11. Closing Remarks

Menir is **lean, auditable, and modular**. It's not trying to be a full ERP; it's a thin event stream + query layer that makes project memory *machine-readable* and *machine-actionable*.

The next frontier is making the graph live (Neo4j), adding intelligence (risk detection), and scaling interactions (API server).

**Ready to build Phase 3?**
