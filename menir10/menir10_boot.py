"""Boot helper for Menir-10 instrumentation.

This module provides lightweight helpers to instrument boot sequences with
Menir-10 logging. It is designed to be called from entrypoints like boot_now.py
and relies on MENIR_PROJECT_ID environment variable to route logs to the correct project.

Usage:
    from menir10.menir10_boot import start_boot_interaction, complete_boot_interaction
    
    state = start_boot_interaction()
    try:
        # ... do boot work ...
        complete_boot_interaction(state, status="ok")
    except Exception as e:
        complete_boot_interaction(state, status="error", extra={"error": str(e)})
"""

import os
from typing import Dict, Any

from .menir10_state import PerceptionState
from .menir10_log import append_log, make_entry


def get_default_project_id() -> str:
    """Get the default project ID from environment or return fallback.
    
    Returns:
        Project ID from MENIR_PROJECT_ID env var, or "personal" if not set.
    """
    return os.environ.get("MENIR_PROJECT_ID", "personal")


def start_boot_interaction(intent_profile: str = "boot_now") -> PerceptionState:
    """Start a boot interaction and log the event.
    
    Args:
        intent_profile: Classification of the boot event (default: "boot_now")
        
    Returns:
        PerceptionState instance with created_at/updated_at set
    """
    project_id = get_default_project_id()
    state = PerceptionState(
        project_id=project_id,
        intent_profile=intent_profile,
    )
    state.start_interaction()
    
    entry = make_entry(
        interaction_id=state.interaction_id,
        project_id=state.project_id,
        intent_profile=state.intent_profile,
        created_at=state.created_at,
        updated_at=state.updated_at,
        flags=state.flags,
        metadata={"stage": "start"},
    )
    append_log(entry)
    
    return state


def complete_boot_interaction(
    state: PerceptionState,
    status: str = "ok",
    extra: Dict[str, Any] | None = None,
) -> None:
    """Complete a boot interaction and log the result.
    
    Args:
        state: PerceptionState from start_boot_interaction()
        status: Status code (default: "ok")
        extra: Optional extra metadata to merge into log entry
    """
    state.touch()
    
    extras = {"stage": "complete", "status": status}
    if extra:
        extras.update(extra)
    
    entry = make_entry(
        interaction_id=state.interaction_id,
        project_id=state.project_id,
        intent_profile=state.intent_profile,
        created_at=state.created_at,
        updated_at=state.updated_at,
        flags=state.flags,
        metadata=extras,
    )
    append_log(entry)
