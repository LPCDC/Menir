# Menir-10 Log Schema

Each line in `logs/menir10_interactions.jsonl` is a JSON object representing one interaction event. Lines are newline-delimited for streaming and line-by-line processing.

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `interaction_id` | string (UUID4) | Unique identifier for this interaction |
| `project_id` | string | Project or context identifier (e.g., "test_menir10", "my_app") |
| `intent_profile` | string | Classification of the interaction type (e.g., "greeting", "query", "boot_now") |
| `created_at` | string (ISO8601) | Timestamp when the interaction started (UTC) |
| `updated_at` | string (ISO8601) | Timestamp of last update (UTC) |
| `flags` | object (dict) | Boolean or other metadata flags keyed by name |

## Optional Fields

Additional fields can be included and will be preserved:
- `metadata` (object): Arbitrary structured data
- `note` (string): Free-form notes
- Any custom field added by the caller

## Example

```json
{
  "interaction_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "test_menir10",
  "intent_profile": "greeting",
  "created_at": "2025-11-26T22:00:00+00:00",
  "updated_at": "2025-11-26T22:00:05+00:00",
  "flags": {
    "success": true,
    "cached": false
  },
  "metadata": {
    "user_id": "joão_001",
    "stage": "start"
  }
}
```

## Usage in Code

```python
from menir10 import make_entry, append_log

entry = make_entry(
    interaction_id="...",
    project_id="test_menir10",
    intent_profile="my_event",
    created_at="2025-11-26T22:00:00+00:00",
    updated_at="2025-11-26T22:00:05+00:00",
    flags={"success": True},
    metadata={"custom": "data"}
)
append_log(entry)
```

All entries are appended to `logs/menir10_interactions.jsonl` in UTF-8 encoding. Parent directories are created automatically.
