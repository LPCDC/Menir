"""Summarize and extract insights from interaction logs."""

import argparse
from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Dict, Any, Tuple

from .menir10_export import load_logs, DEFAULT_LOG_PATH


def get_logs(log_path: Path | str | None = None) -> List[Dict[str, Any]]:
    """Load logs (delegates to load_logs).
    
    Args:
        log_path: Path to log file. If None, use DEFAULT_LOG_PATH.
        
    Returns:
        List of log entry dictionaries.
    """
    return load_logs(log_path)


def group_by_project(logs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group log entries by project_id.
    
    Args:
        logs: List of log entries
        
    Returns:
        Dictionary mapping project_id to list of entries
    """
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for entry in logs:
        project_id = entry.get("project_id", "unknown")
        grouped[project_id].append(entry)
    return dict(grouped)


def list_top_projects(logs: List[Dict[str, Any]], top_n: int = 5) -> List[Tuple[str, int]]:
    """Get the most common projects by interaction count.
    
    Args:
        logs: List of log entries
        top_n: Number of top projects to return (default: 5)
        
    Returns:
        List of (project_id, count) tuples, sorted by count descending
    """
    project_ids = [entry.get("project_id", "unknown") for entry in logs]
    counter = Counter(project_ids)
    return counter.most_common(top_n)


def summarize_project(
    project_id: str,
    logs: List[Dict[str, Any]],
    limit: int = 50,
) -> Dict[str, Any]:
    """Summarize interactions for a specific project.
    
    Args:
        project_id: Project identifier to filter by
        logs: List of all log entries
        limit: Maximum number of interactions to include (default: 50)
        
    Returns:
        Dictionary with project summary
    """
    # Filter logs for this project
    project_logs = [
        entry for entry in logs
        if entry.get("project_id", "unknown") == project_id
    ]
    
    # Sort by created_at if available
    def get_sort_key(entry: Dict[str, Any]) -> str:
        return entry.get("created_at", "")
    
    sorted_logs = sorted(project_logs, key=get_sort_key)
    
    # Slice to limit
    sampled = sorted_logs[:limit]
    
    return {
        "project_id": project_id,
        "total_count": len(project_logs),
        "sample_count": len(sampled),
        "interactions": sampled,
    }


def render_project_context(summary: Dict[str, Any]) -> str:
    """Render project summary as GPT-ready context block.
    
    Args:
        summary: Project summary from summarize_project()
        
    Returns:
        Human-readable context string
    """
    lines = []
    
    project_id = summary.get("project_id", "unknown")
    total_count = summary.get("total_count", 0)
    sample_count = summary.get("sample_count", 0)
    interactions = summary.get("interactions", [])
    
    # Header
    lines.append(f"Project: {project_id}")
    lines.append(f"Total interactions: {total_count} | Showing: {sample_count}")
    lines.append("")
    
    # Interactions
    if interactions:
        lines.append("Interactions:")
        for interaction in interactions:
            created_at = interaction.get("created_at", "?")
            intent_profile = interaction.get("intent_profile", "?")
            flags = interaction.get("flags", {})
            flags_str = ", ".join(f"{k}={v}" for k, v in flags.items()) if flags else "no flags"
            
            line = f"- {created_at} | intent={intent_profile} | flags={{{flags_str}}}"
            lines.append(line)
            
            # Include metadata.content if present
            metadata = interaction.get("metadata", {})
            content = metadata.get("content", "")
            if content:
                lines.append(f"  Content: {content}")
    else:
        lines.append("(no interactions)")
    
    return "\n".join(lines)


def main() -> None:
    """Parse CLI arguments and dispatch to subcommands."""
    parser = argparse.ArgumentParser(
        description="Extract insights from Menir-10 interaction logs"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Subcommand: top
    top_parser = subparsers.add_parser("top", help="List top projects by interaction count")
    top_parser.add_argument(
        "--log-path",
        type=str,
        default=None,
        help="Path to log file (default: logs/menir10_interactions.jsonl)",
    )
    top_parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of top projects to show (default: 5)",
    )
    
    # Subcommand: context
    context_parser = subparsers.add_parser("context", help="Render context for a project")
    context_parser.add_argument("project_id", help="Project ID to summarize")
    context_parser.add_argument(
        "--log-path",
        type=str,
        default=None,
        help="Path to log file (default: logs/menir10_interactions.jsonl)",
    )
    context_parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum interactions to show (default: 20)",
    )
    
    args = parser.parse_args()
    
    if args.command == "top":
        logs = get_logs(args.log_path)
        if not logs:
            print("No logs found.")
            exit(1)
        
        top_projects = list_top_projects(logs, top_n=args.top_n)
        for project_id, count in top_projects:
            print(f"{project_id} {count}")
    
    elif args.command == "context":
        logs = get_logs(args.log_path)
        summary = summarize_project(args.project_id, logs, limit=args.limit)
        
        if summary["sample_count"] == 0:
            print(f"No interactions found for project: {args.project_id}")
            exit(1)
        
        context = render_project_context(summary)
        print(context)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
