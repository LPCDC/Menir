from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

LOG_PATH = Path("logs/menir10_interactions.jsonl")


class MissingProjectIdError(RuntimeError):
    """Lançada quando MENIR_PROJECT_ID não está definido."""
    pass


def get_project_id(explicit: Optional[str] = None) -> str:
    project_id = explicit or os.getenv("MENIR_PROJECT_ID")
    if not project_id:
        raise MissingProjectIdError(
            "MENIR_PROJECT_ID obrigatório para log Menir-10."
        )
    return project_id


def append_log(
    *,
    project_id: Optional[str] = None,
    intent_profile: str,
    content: str,
    flags: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    log_path: Path = LOG_PATH,
) -> Dict[str, Any]:
    pid = get_project_id(project_id)
    now = datetime.now(timezone.utc).isoformat()

    record: Dict[str, Any] = {
        "interaction_id": str(uuid.uuid4()),
        "project_id": pid,
        "intent_profile": intent_profile,
        "created_at": now,
        "updated_at": now,
        "flags": flags or {},
        "metadata": {
            "stage": "single",
            "status": "ok",
            **(metadata or {}),
            "content": content,
        },
    }

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record


def make_entry(
    interaction_id: str,
    project_id: str,
    intent_profile: str,
    created_at: str,
    updated_at: str,
    flags: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create a log entry dictionary (compatibility helper).

    Returns a dictionary matching the JSONL schema used by Menir-10.
    """
    entry: Dict[str, Any] = {
        "interaction_id": interaction_id,
        "project_id": project_id,
        "intent_profile": intent_profile,
        "created_at": created_at,
        "updated_at": updated_at,
        "flags": flags,
    }
    if metadata is not None:
        entry["metadata"] = metadata
    return entry

