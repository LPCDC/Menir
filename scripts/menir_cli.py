
import sys
import argparse
import subprocess
import json
from pathlib import Path

# Add project root to path for imports if needed, though we primarily use subprocess for scripts
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from menir_core.rag.tasks import get_project_state, list_open_tasks

def run_script(script_name):
    script_path = BASE_DIR / "scripts" / script_name
    try:
        # Use sys.executable to ensure we use the same python interpreter
        subprocess.run([sys.executable, str(script_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_name}: {e}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

def cmd_boot(args):
    print("🚀 Initializing Menir Boot Sequence...")
    run_script("boot_menir.py")

def cmd_shutdown(args):
    print("🛑 Initiating Menir Shutdown Sequence...")
    run_script("shutdown_menir.py")

def cmd_health(args):
    print("🏥 Running Health Check...")
    # Import and run directly or subprocess? Subprocess is safer for independence
    run_script("menir_health.py")

def cmd_open(args):
    project = args.project_id
    print(f"📂 Open Tasks for {project.upper()}:")
    tasks = list_open_tasks(project)
    if not tasks:
        print("   (No open tasks found)")
    else:
        for t in tasks:
            print(f"   [ ] {t['task_id']}: {t['description']} ({t['age_days']} days)")

def cmd_summary(args):
    project = args.project_id
    print(f"📊 Project Summary: {project.upper()}")
    state = get_project_state(project)
    if "error" in state:
        print(f"   ❌ Error: {state['error']['message']}")
        return

    info = state.get("project_info", {})
    stats = state.get("tasks_stats", {})
    
    print(f"   Status: {info.get('status', 'UNKNOWN')}")
    print(f"   Open Tasks: {stats.get('open_count', 0)}")
    print(f"   Done Tasks: {stats.get('done_count', 0)}")
    
    print("\n   Recent Activity:")
    for sess in state.get("recent_activity", []):
         print(f"   - {sess.get('started_at', '')[:10]}: {sess.get('exit_summary', '')[:50]}...")

def main():
    parser = argparse.ArgumentParser(description="Menir v1.1 Unified CLI", prog="menir")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # boot
    subparsers.add_parser("boot", help="Start a new work session")
    
    # shutdown
    subparsers.add_parser("shutdown", help="End current work session")
    
    # health
    subparsers.add_parser("health", help="Check system health")
    
    # open <project>
    open_parser = subparsers.add_parser("open", help="List open tasks for a project")
    open_parser.add_argument("project_id", help="Project ID (e.g., debora)")
    
    # summary <project>
    sum_parser = subparsers.add_parser("summary", help="Show project status summary")
    sum_parser.add_argument("project_id", help="Project ID")

    args = parser.parse_args()

    if args.command == "boot":
        cmd_boot(args)
    elif args.command == "shutdown":
        cmd_shutdown(args)
    elif args.command == "health":
        cmd_health(args)
    elif args.command == "open":
        cmd_open(args)
    elif args.command == "summary":
        cmd_summary(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
