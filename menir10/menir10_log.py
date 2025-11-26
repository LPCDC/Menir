"""JSONL logger for interaction logging."""

import json
from pathlib import Path
from typing import Dict, Any


LOG_PATH = Path("logs/menir10_interactions.jsonl")


def append_log(entry: Dict[str, Any]) -> None:
    """Append a JSON entry to the JSONL log file.
    
    Args:
        entry: Dictionary to serialize and append to log
    """
    # Ensure parent directory exists
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Append entry as JSON line
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False)
        f.write("\n")


def make_entry(
    interaction_id: str,
    project_id: str,
    intent_profile: str,
    created_at: str,
    updated_at: str,
    flags: Dict[str, bool],
    metadata: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Create a log entry dictionary.
    
    Args:
        interaction_id: Unique interaction identifier
        project_id: Project identifier
        intent_profile: Intent profile name
        created_at: ISO8601 creation timestamp
        updated_at: ISO8601 update timestamp
        flags: Dictionary of boolean flags
        metadata: Optional additional metadata
        
    Returns:
        Dictionary ready for serialization
    """
    entry = {
        "interaction_id": interaction_id,
        "project_id": project_id,
        "intent_profile": intent_profile,
        "created_at": created_at,
        "updated_at": updated_at,
        "flags": flags,
    }
    if metadata:
        entry["metadata"] = metadata
    return entry
