# Test Menir10 Project

The `test_menir10` project is a **synthetic sandbox** for experimenting with Menir-10 logging and insights without touching real data.

## Story

**Scenario**: A hypothetical property/banking scenario with four entities:

- **João**: A user seeking property financing
- **Maria**: João's business partner
- **Banco Delta**: A fictional bank providing loans
- **Otávio**: A lawyer handling documentation

**Example Interactions**:
1. João logs in and requests a loan (intent: "greeting", "query")
2. Maria reviews the application (intent: "review")
3. Otávio prepares documents (intent: "document_prep")
4. Banco Delta approves the loan (intent: "approval")

None of these entities or interactions are real. They exist only to demonstrate logging patterns and context generation.

## How to Use

### 1. Set the Environment Variable

```bash
export MENIR_PROJECT_ID=test_menir10
```

### 2. Log an Interaction

```python
from menir10 import PerceptionState, make_entry, append_log

state = PerceptionState(
    project_id="test_menir10",
    intent_profile="greeting"
)
state.start_interaction()
entry = make_entry(**state.to_dict())
append_log(entry)
```

Or, if you have boot instrumentation wired:

```bash
export MENIR_PROJECT_ID=test_menir10
python scripts/boot_now.py
```

### 3. Query the Project

```bash
python -m menir10.menir10_insights context test_menir10 --limit 20
```

Output:
```
Project: test_menir10
Total interactions: 4 | Showing: 4

Interactions:
- 2025-11-26T22:00:00+00:00 | intent=greeting | flags={no flags}
- 2025-11-26T22:01:00+00:00 | intent=review | flags={no flags}
- 2025-11-26T22:02:00+00:00 | intent=document_prep | flags={no flags}
- 2025-11-26T22:03:00+00:00 | intent=approval | flags={no flags}
```

### 4. See All Projects

```bash
python -m menir10.menir10_insights top
```

## Notes

- **No Real Data**: All entities and interactions in this story are fictional.
- **Safe Experimentation**: Use `test_menir10` to learn the logging API without risk.
- **Easy Cleanup**: Delete logs for this project by filtering in the JSONL file or re-initializing logs.

For details on the schema, see [MENIR10_LOG_SCHEMA.md](MENIR10_LOG_SCHEMA.md).
