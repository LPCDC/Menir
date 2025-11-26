# Menir-10: Local Psych Engine

Menir-10 is a minimal "psych engine" that logs interactions locally to JSONL format and can export them to Neo4j via Cypher scripts. It provides a foundation for recording, summarizing, and understanding interaction patterns across projects without external dependencies.

## Core Modules

- **menir10_state**: `PerceptionState` class that encapsulates per-interaction state with timestamps and metadata.
- **menir10_log**: JSONL-based logger that appends entries to `logs/menir10_interactions.jsonl` and provides entry factories.
- **menir10_export**: Loads logs from disk and generates Cypher `CREATE` statements for Neo4j import.
- **menir10_insights**: Groups logs by project, computes statistics, summarizes interactions, and renders GPT-ready context blocks. Includes CLI subcommands.

## Quick Start

### 1. Create a PerceptionState

```python
from menir10 import PerceptionState, make_entry, append_log

state = PerceptionState(
    project_id="my_project",
    intent_profile="greeting"
)
```

### 2. Start the Interaction

```python
state.start_interaction()  # Sets created_at and updated_at to now
```

### 3. Log the Entry

```python
entry = make_entry(
    interaction_id=state.interaction_id,
    project_id=state.project_id,
    intent_profile=state.intent_profile,
    created_at=state.created_at,
    updated_at=state.updated_at,
    flags=state.flags,
    metadata={"custom_field": "value"}  # optional
)
append_log(entry)
```

### 4. Extract Insights

```python
from menir10 import load_logs, summarize_project, render_project_context

logs = load_logs()
summary = summarize_project("my_project", logs, limit=20)
context = render_project_context(summary)
print(context)  # GPT-ready text
```

## CLI

```bash
# List top projects
python -m menir10.menir10_insights top --top-n 5

# Render context for a project
python -m menir10.menir10_insights context my_project --limit 20

# Export to Cypher
python -m menir10.menir10_export

# Daily report (markdown)
python scripts/menir10_daily_report.py --top-n 3 --limit 20 --out daily_context.md
```

## Log Schema

See [docs/MENIR10_LOG_SCHEMA.md](MENIR10_LOG_SCHEMA.md) for details on the JSONL format.

## Test Project

For safe experimentation without affecting real data, see [docs/PROJECT_TEST_MENIR10.md](PROJECT_TEST_MENIR10.md).
