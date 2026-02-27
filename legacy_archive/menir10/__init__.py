"""Menir-10: minimal interaction logging with PerceptionState."""

from menir10.menir10_state import PerceptionState
from menir10.menir10_log import append_log, make_entry
from menir10.menir10_export import (
    load_logs,
    generate_cypher_interactions,
)
from menir10.menir10_insights import (
    get_logs,
    group_by_project,
    list_top_projects,
    summarize_project,
    render_project_context,
)
from menir10.menir10_boot import (
    get_default_project_id,
    start_boot_interaction,
    complete_boot_interaction,
)


__version__ = "0.1.0"
__all__ = [
    "PerceptionState",
    "append_log",
    "make_entry",
    "load_logs",
    "generate_cypher_interactions",
    "get_logs",
    "group_by_project",
    "list_top_projects",
    "summarize_project",
    "render_project_context",
    "get_default_project_id",
    "start_boot_interaction",
    "complete_boot_interaction",
]
