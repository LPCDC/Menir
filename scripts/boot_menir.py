
import json
import uuid
import datetime
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
SESSIONS_FILE = BASE_DIR / "data" / "system" / "menir_sessions.jsonl"
TASKS_FILE = BASE_DIR / "data" / "system" / "menir_tasks.jsonl"
STATE_FILE = BASE_DIR / ".menir_state"

def load_jsonl(path):
    data = []
    if not path.exists():
        return data
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return data

def save_jsonl_append(path, record):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")

def get_open_tasks():
    tasks = load_jsonl(TASKS_FILE)
    return [t for t in tasks if t.get("status") not in ["DONE", "ARCHIVED"]]

def check_last_session():
    sessions = load_jsonl(SESSIONS_FILE)
    if not sessions:
        return None, "FIRST_RUN"
    last = sessions[-1]
    if last.get("state") == "OPEN":
        return last, "CRASHED"
    return last, "CLEAN"

def main():
    print("\n🖥️  MENIR SYSTEM BOOT [v1.0]")
    print("=========================================")

    # 1. Check Previous State
    last_session, status = check_last_session()
    
    if status == "CRASHED":
        print(f"⚠️  WARNING: Last session ({last_session['session_id'][:8]}...) was not closed properly.")
        print("   -> Assuming crash or forced exit.")
    elif status == "FIRST_RUN":
        print("🌱  Welcome. This is the first recorded session.")
    else:
        print(f"✅ Last available session closed at: {last_session.get('timestamp_end', 'Unknown')}")

    # 2. Load Context (Tasks)
    open_tasks = get_open_tasks()
    print(f"\n📂 Context Loading:")
    print(f"   - Active Anchor Projects: [debora, menir_core]")
    print(f"   - Pending Tasks: {len(open_tasks)}")
    
    if open_tasks:
        print("\n📝 Backlog Snapshot:")
        for t in open_tasks[:5]:
            print(f"   [ ] {t.get('project', 'general').upper()}: {t.get('description')} ({t.get('status')})")
        if len(open_tasks) > 5:
            print(f"   ... and {len(open_tasks) - 5} more.")

    # 3. Create New Session
    session_id = str(uuid.uuid4())
    start_time = datetime.datetime.utcnow().isoformat() + "Z"
    
    new_session = {
        "session_id": session_id,
        "timestamp_start": start_time,
        "timestamp_end": None,
        "operator": os.getenv("USERNAME", "User"),
        "context": {
            "focus_project": "debora", # Default, could be arg
            "active_anchors": ["menir_core", "debora"]
        },
        "state": "OPEN",
        "exit_summary": None
    }
    
    # 4. Persist
    save_jsonl_append(SESSIONS_FILE, new_session)
    
    # Save State for Shutdown script
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"current_session_id": session_id}, f)

    print("\n🚀 Session Initiated.")
    print(f"   ID: {session_id}")
    print(f"   Timestamp: {start_time}")
    
    # 5. Sync Graph
    try:
        from scripts.sync_system_graph import sync_graph
        sync_graph()
    except Exception as e:
        print(f"⚠️  Graph Sync Warning: {e}")
        
    print("=========================================\n")

if __name__ == "__main__":
    main()
