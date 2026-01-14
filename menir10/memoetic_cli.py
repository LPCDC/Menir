import argparse
import sys

# CORRECTION: Define stubs instead of exiting, ensuring CLI always runs
try:
    from menir10.menir10_insights import get_logs, summarize_project, render_project_context
except ImportError:
    print("⚠️  Running in stub mode (menir10_insights not found)")
    def get_logs(): return []
    def summarize_project(*args, **kwargs): return {"sample_count": 0}
    def render_project_context(*args): return ""

def main():
    parser = argparse.ArgumentParser(description="Menir Memoetic CLI")
    parser.add_argument("--project", required=True)
    parser.add_argument("--mode", default="summary")
    args = parser.parse_args()
    
    logs = get_logs()
    summary = summarize_project(args.project, logs, limit=50)
    
    print(f"--- 📝 Summary: {args.project} ---")
    if summary.get("sample_count", 0) > 0:
        print(render_project_context(summary))
    else:
        print(f"No logs found for {args.project}. Ready for ingestion.")

if __name__ == "__main__":
    main()
