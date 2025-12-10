
import json
import datetime
import uuid
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

def save_jsonl_rewrite(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for record in data:
            f.write(json.dumps(record, default=str) + "\n")

def save_jsonl_append(path, record):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")

def get_current_session_id():
    if not STATE_FILE.exists():
        return None
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return data.get("current_session_id")
    except:
        return None

def main():
    print("\n🛑 MENIR SYSTEM SHUTDOWN")
    print("=========================================")
    
    session_id = get_current_session_id()
    if not session_id:
        print("❌ No active session found in .menir_state.")
        print("   - Using manual recovery mode? (Not implemented)")
        return

    print(f"📍 Closing Session: {session_id}")
    
    # 1. The Ritual: Synthesis
    print("\n📝 Session Summary (The 'Ritual'):")
    summary = input("   > What was accomplished/decided? ")
    
    # 2. Task Promotion
    print("\n📋 Task Promotion (Add to Backlog):")
    print("   Enter tasks in format: 'PROJECT: Description' (or empty to finish)")
    
    new_tasks = []
    while True:
        entry = input("   > Task: ")
        if not entry.strip():
            break
        
        # Simple Parse
        if ":" in entry:
            proj, desc = entry.split(":", 1)
        else:
            proj = "general"
            desc = entry
            
        task_id = f"TASK-{uuid.uuid4().hex[:6].upper()}"
        task = {
            "task_id": task_id,
            "project": proj.strip().lower(),
            "status": "OPEN",
            "priority": "MEDIUM",
            "description": desc.strip(),
            "lifecycle": {
                "created_at": datetime.datetime.utcnow().isoformat() + "Z",
                "created_in_session": session_id,
                "completed_at": None
            }
        }
        new_tasks.append(task)
        print(f"     -> Added {task_id}")

    # 3. Persist Tasks
    for t in new_tasks:
        save_jsonl_append(TASKS_FILE, t)
    print(f"✅ {len(new_tasks)} items promoted to Log.")

    # 4. Close Session
    sessions = load_jsonl(SESSIONS_FILE)
    updated = False
    for s in sessions:
        if s["session_id"] == session_id:
            s["state"] = "CLOSED"
            s["timestamp_end"] = datetime.datetime.utcnow().isoformat() + "Z"
            s["exit_summary"] = summary
            updated = True
            break
    
    if updated:
        save_jsonl_rewrite(SESSIONS_FILE, sessions)
        print("✅ Session Closed.")
    else:
        print("❌ Error: Session ID not found in logs. Audit corrupted.")

    # 4.5 Sync Graph
    try:
        from scripts.sync_system_graph import sync_graph
        sync_graph()
    except Exception as e:
        print(f"⚠️  Graph Sync Warning: {e}")

    # 5. Cleanup
    if STATE_FILE.exists():
        os.remove(STATE_FILE)
    
    print("=========================================")
    print("👋 System Offline.\n")

if __name__ == "__main__":
    main()
