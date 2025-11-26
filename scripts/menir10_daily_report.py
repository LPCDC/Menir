"""Generate daily Markdown report from Menir-10 logs."""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path so we can import menir10
sys.path.insert(0, str(Path(__file__).parent.parent))

from menir10.menir10_insights import (
    get_logs,
    list_top_projects,
    summarize_project,
    render_project_context,
)


def build_daily_report(
    log_path: str | None = None,
    top_n: int = 3,
    limit: int = 20,
) -> str:
    """Build a daily Markdown report from logs.
    
    Args:
        log_path: Optional path to log file. If None, uses default.
        top_n: Number of top projects to include (default: 3)
        limit: Max interactions per project (default: 20)
        
    Returns:
        Markdown string with daily context
    """
    logs = get_logs(log_path)
    
    if not logs:
        return "No Menir-10 logs found."
    
    lines = ["# Menir-10 Daily Context", ""]
    
    top_projects = list_top_projects(logs, top_n=top_n)
    
    for project_id, count in top_projects:
        summary = summarize_project(project_id, logs, limit=limit)
        context = render_project_context(summary)
        
        lines.append(f"## {project_id}")
        lines.append("")
        lines.append(context)
        lines.append("")
    
    return "\n".join(lines)


def main() -> None:
    """Parse CLI args and generate report."""
    parser = argparse.ArgumentParser(
        description="Generate daily Menir-10 context report"
    )
    parser.add_argument(
        "--log-path",
        type=str,
        default=None,
        help="Path to log file (default: logs/menir10_interactions.jsonl)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=3,
        help="Number of top projects to include (default: 3)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Max interactions per project (default: 20)",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Output file path. If omitted, print to stdout.",
    )
    
    args = parser.parse_args()
    
    report = build_daily_report(
        log_path=args.log_path,
        top_n=args.top_n,
        limit=args.limit,
    )
    
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report written to {out_path}")
    else:
        print(report)


if __name__ == "__main__":
    main()
