
import sys
import json
import argparse
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from menir_core.rag.tasks import query_tasks_graph

def main():
    parser = argparse.ArgumentParser(description="Menir Task Graph Query CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Command: open
    open_parser = subparsers.add_parser("open", help="List open tasks for a project")
    open_parser.add_argument("project_id", help="Project ID (e.g., debora, menir_core)")

    # Command: summary
    summary_parser = subparsers.add_parser("summary", help="Get project summary")
    summary_parser.add_argument("project_id", help="Project ID")

    # Command: last
    last_parser = subparsers.add_parser("last", help="Get tasks from last session")
    
    # Command: stale
    stale_parser = subparsers.add_parser("stale", help="Find stale tasks")
    stale_parser.add_argument("--days", type=int, default=7, help="Minimum age in days")
    stale_parser.add_argument("--project", help="Optional project filter")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    result = {}
    
    if args.command == "open":
        result = query_tasks_graph("PROJECT_OPEN_TASKS", project_id=args.project_id)
    
    elif args.command == "summary":
        result = query_tasks_graph("PROJECT_SUMMARY", project_id=args.project_id)
    
    elif args.command == "last":
        result = query_tasks_graph("LAST_SESSION_TASKS", session_ref="last")
        
    elif args.command == "stale":
        result = query_tasks_graph("STALE_TASKS", min_age_days=args.days, project_id=args.project)

    # Output Result
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    main()
