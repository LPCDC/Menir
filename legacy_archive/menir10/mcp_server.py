#!/usr/bin/env python
"""
MCP Contextual Proxy Server (Menir v10.3)

Extends the base MCP server with project context awareness.
Automatically injects project metadata and interaction history into responses.

Methods:
- ping: Health check
- boot_now: Boot state with repo context
- context: Project context (interactions, metadata, insights)
- project_summary: Summary of project by ID
- list_projects: List all registered projects
- search_interactions: Search interactions by project/time/flags

Features:
- Automatic context injection for project-aware requests
- JSONL logging of all operations (mcp_operations.jsonl)
- Safe error handling and graceful degradation
- Memory-efficient streaming of large datasets
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Iterator
import re

# Canonical modules from menir10 package
try:
    from menir10.menir10_log import get_project_id
    from menir10.menir10_insights import (
        get_logs,
        group_by_project,
        list_top_projects,
        summarize_project,
        render_project_context,
    )
    from menir10.menir10_state import PerceptionState
except ImportError as e:
    print(f"⚠️ Warning: Could not import menir10 modules: {e}", file=sys.stderr)
    # Fallback definitions (minimal)
    def get_project_id(project_id: str | None = None) -> str:
        import os
        return project_id or os.getenv("MENIR_PROJECT_ID", "unknown")
    
    def get_logs(log_path: Path) -> List[dict]:
        return []
    
    def group_by_project(logs: List[dict]) -> Dict[str, List[dict]]:
        return {}
    
    def list_top_projects(logs: List[dict], top_n: int = 10) -> List[tuple]:
        return []
    
    def summarize_project(project_id: str, logs: List[dict]) -> dict:
        return {"project_id": project_id, "count": 0}
    
    def render_project_context(project_id: str, logs: List[dict], limit: int = 20) -> str:
        return f"# Context for {project_id}\n\nNo interactions found."

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
LOG_PATH = REPO_ROOT / "mcp_operations.jsonl"
MENIR_STATE_PATH = REPO_ROOT / "menir_state.json"
INTERACTIONS_LOG_PATH = REPO_ROOT / "logs" / "menir10_interactions.jsonl"

MAX_TEXT_BYTES = 64000
MAX_INTERACTIONS_RETURNED = 100


def log_event(event: Dict[str, Any]) -> None:
    """Append event to mcp_operations.jsonl (best-effort)."""
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            json.dump(event, f, ensure_ascii=False)
            f.write("\n")
    except Exception:
        pass


def safe_read_text(path: Path, max_bytes: int = MAX_TEXT_BYTES) -> Optional[str]:
    """Safely read file content up to max_bytes."""
    if not path.exists():
        return None
    try:
        data = path.read_bytes()[:max_bytes]
        return data.decode("utf-8", errors="replace")
    except Exception:
        return None


def load_menir_state() -> Dict[str, Any]:
    """Load menir_state.json (project registry)."""
    if not MENIR_STATE_PATH.exists():
        return {"projects": {}}
    try:
        return json.loads(MENIR_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"projects": {}}


def load_interactions() -> List[dict]:
    """Load all interactions from JSONL log."""
    if not INTERACTIONS_LOG_PATH.exists():
        return []
    
    interactions = []
    try:
        with INTERACTIONS_LOG_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        interactions.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    except Exception:
        pass
    
    return interactions


def handle_ping(params: Dict[str, Any] | None) -> Dict[str, Any]:
    """Health check."""
    return {
        "status": "Menir-10 contextual proxy alive",
        "version": "10.3",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def handle_boot_now(params: Dict[str, Any] | None) -> Dict[str, Any]:
    """Boot state with enhanced context."""
    now = datetime.now(timezone.utc).isoformat()
    
    last_boot_path = REPO_ROOT / "last_boot_now.json"
    last_boot_raw = safe_read_text(last_boot_path)
    
    menir_plan_path = REPO_ROOT / "MENIR_PLAN.md"
    menir_plan_raw = safe_read_text(menir_plan_path)
    menir_plan_excerpt = menir_plan_raw[:8000] if menir_plan_raw else None
    
    # Load project context
    menir_state = load_menir_state()
    project_count = len(menir_state.get("projects", {}))
    
    # Load interaction stats
    interactions = load_interactions()
    interaction_count = len(interactions)
    
    notes = []
    if last_boot_raw:
        notes.append("last_boot_now.json found in repo root.")
    if menir_plan_raw:
        notes.append("MENIR_PLAN.md found; excerpt included.")
    if project_count > 0:
        notes.append(f"Menir state: {project_count} projects registered.")
    if interaction_count > 0:
        notes.append(f"Menir logs: {interaction_count} interactions recorded.")
    
    return {
        "timestamp": now,
        "repo_root": str(REPO_ROOT),
        "last_boot_now": last_boot_raw,
        "menir_plan_excerpt": menir_plan_excerpt,
        "projects_count": project_count,
        "interactions_count": interaction_count,
        "notes": notes,
    }


def handle_context(params: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Retrieve project context (interactions, metadata, insights).
    
    Params:
    - project_id (required): project identifier
    - limit (optional): max interactions to return (default: 20)
    - include_markdown (optional): return rendered markdown context (default: true)
    """
    if not params:
        return {"error": "context requires params", "params_needed": ["project_id"]}
    
    project_id = params.get("project_id")
    if not project_id:
        return {"error": "project_id is required"}
    
    limit = params.get("limit", 20)
    include_markdown = params.get("include_markdown", True)
    
    # Load interactions and state
    interactions = load_interactions()
    menir_state = load_menir_state()
    
    # Filter interactions for this project
    project_interactions = [
        i for i in interactions
        if i.get("project_id") == project_id
    ]
    
    # Project metadata
    project_meta = menir_state.get("projects", {}).get(project_id, {})
    
    # Recent interactions (most recent first)
    recent = sorted(
        project_interactions[-limit:],
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )
    
    result = {
        "project_id": project_id,
        "metadata": project_meta,
        "interaction_count": len(project_interactions),
        "recent_interactions": recent,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    # Add markdown context if requested
    if include_markdown:
        try:
            # render_project_context expects a summary dict
            summary = summarize_project(project_id, interactions)
            markdown_context = render_project_context(summary)
            result["markdown_context"] = markdown_context
        except Exception as e:
            # Gracefully handle rendering errors
            result["markdown_context"] = f"# Context for {project_id}\n\nError rendering context: {str(e)}"
    
    return result


def handle_project_summary(params: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Get project summary (count, dates, status).
    
    Params:
    - project_id (required): project identifier
    """
    if not params:
        return {"error": "project_summary requires params", "params_needed": ["project_id"]}
    
    project_id = params.get("project_id")
    if not project_id:
        return {"error": "project_id is required"}
    
    # Load data
    interactions = load_interactions()
    menir_state = load_menir_state()
    
    # Filter for this project
    project_interactions = [
        i for i in interactions
        if i.get("project_id") == project_id
    ]
    
    project_meta = menir_state.get("projects", {}).get(project_id, {})
    
    # Calculate stats
    if project_interactions:
        dates = sorted([i.get("created_at", "") for i in project_interactions])
        first_interaction = dates[0]
        last_interaction = dates[-1]
    else:
        first_interaction = None
        last_interaction = None
    
    # Group by intent profile
    intent_counts = {}
    for interaction in project_interactions:
        intent = interaction.get("intent_profile", "unknown")
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
    
    return {
        "project_id": project_id,
        "name": project_meta.get("name", project_id),
        "status": project_meta.get("status", "unknown"),
        "category": project_meta.get("category", ""),
        "interaction_count": len(project_interactions),
        "first_interaction": first_interaction,
        "last_interaction": last_interaction,
        "intent_profile_distribution": intent_counts,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def handle_list_projects(params: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    List all registered projects with counts.
    
    Params:
    - top_n (optional): return top N projects by interaction count (default: all)
    """
    # Load data
    interactions = load_interactions()
    menir_state = load_menir_state()
    
    top_n = params.get("top_n") if params else None
    
    # Group by project
    project_counts = {}
    for interaction in interactions:
        project_id = interaction.get("project_id", "unknown")
        project_counts[project_id] = project_counts.get(project_id, 0) + 1
    
    # Sort by count
    sorted_projects = sorted(
        project_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    if top_n:
        sorted_projects = sorted_projects[:top_n]
    
    # Enrich with metadata
    projects_list = []
    for project_id, count in sorted_projects:
        meta = menir_state.get("projects", {}).get(project_id, {})
        projects_list.append({
            "project_id": project_id,
            "name": meta.get("name", project_id),
            "status": meta.get("status", "unknown"),
            "interaction_count": count,
        })
    
    return {
        "projects": projects_list,
        "total_projects": len(projects_list),
        "total_interactions": len(interactions),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def handle_search_interactions(params: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Search interactions by project, intent profile, or date range.
    
    Params:
    - project_id (optional): filter by project
    - intent_profile (optional): filter by intent profile
    - since (optional): ISO8601 timestamp (inclusive)
    - until (optional): ISO8601 timestamp (inclusive)
    - limit (optional): max results (default: 100)
    """
    if not params:
        params = {}
    
    interactions = load_interactions()
    
    # Apply filters
    results = interactions
    
    project_id = params.get("project_id")
    if project_id:
        results = [i for i in results if i.get("project_id") == project_id]
    
    intent_profile = params.get("intent_profile")
    if intent_profile:
        results = [i for i in results if i.get("intent_profile") == intent_profile]
    
    since = params.get("since")
    if since:
        results = [i for i in results if i.get("created_at", "") >= since]
    
    until = params.get("until")
    if until:
        results = [i for i in results if i.get("created_at", "") <= until]
    
    # Sort by date (most recent first)
    results = sorted(
        results,
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )
    
    # Apply limit
    limit = params.get("limit", 100)
    results = results[:limit]
    
    return {
        "query_params": {
            "project_id": project_id,
            "intent_profile": intent_profile,
            "since": since,
            "until": until,
            "limit": limit,
        },
        "results": results,
        "result_count": len(results),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


METHODS = {
    "ping": handle_ping,
    "boot_now": handle_boot_now,
    "context": handle_context,
    "project_summary": handle_project_summary,
    "list_projects": handle_list_projects,
    "search_interactions": handle_search_interactions,
}


def main() -> None:
    """Main JSON-RPC 2.0 server loop."""
    print("MCP contextual proxy server ready (Menir v10.3)", file=sys.stderr, flush=True)
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        
        jsonrpc = req.get("jsonrpc")
        method = req.get("method")
        req_id = req.get("id")
        params = req.get("params")
        
        # Log request
        log_event({
            "ts": datetime.now(timezone.utc).isoformat() + "Z",
            "direction": "in",
            "request": req,
        })
        
        # Process request
        if jsonrpc != "2.0":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32600, "message": "Invalid Request: jsonrpc must be 2.0"},
            }
        elif method not in METHODS:
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
        else:
            try:
                result = METHODS[method](params)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": result,
                }
            except Exception as e:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                }
        
        # Log response
        log_event({
            "ts": datetime.now(timezone.utc).isoformat() + "Z",
            "direction": "out",
            "response": resp,
        })
        
        # Send response
        print(json.dumps(resp, ensure_ascii=False))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
