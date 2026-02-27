
import json
import os
import sys
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Config
BASE_DIR = Path(__file__).parent.parent
SESSIONS_FILE = BASE_DIR / "data" / "system" / "menir_sessions.jsonl"
TASKS_FILE = BASE_DIR / "data" / "system" / "menir_tasks.jsonl"

load_dotenv(override=True)

# Pre-defined Anchors (could be moved to a file later)
ANCHOR_PROJECTS = [
    {"id": "debora", "name": "Livro Débora", "status": "ACTIVE"},
    {"id": "menir_core", "name": "Menir Core System", "status": "ACTIVE"},
    {"id": "general", "name": "General Context", "status": "ACTIVE"}
]

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

def get_driver():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "menir123")
    if not password:
        print("⚠️  Warning: NEO4J_PASSWORD not found.")
    return GraphDatabase.driver(uri, auth=(user, password))

def sync_graph():
    print("🔄 Syncing System Graph...")
    
    # 1. Load Data
    sessions = load_jsonl(SESSIONS_FILE)
    tasks = load_jsonl(TASKS_FILE)
    print(f"   - Found {len(sessions)} sessions")
    print(f"   - Found {len(tasks)} tasks")

    driver = get_driver()
    processed_nodes = 0
    processed_rels = 0

    with driver.session() as session:
        # 2. Constraints
        session.run("CREATE CONSTRAINT session_id_unique IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE")
        session.run("CREATE CONSTRAINT task_id_unique IF NOT EXISTS FOR (t:Task) REQUIRE t.task_id IS UNIQUE")
        session.run("CREATE CONSTRAINT project_id_unique IF NOT EXISTS FOR (p:Project) REQUIRE p.project_id IS UNIQUE")

        # 3. Sync Anchors (Projects)
        for proj in ANCHOR_PROJECTS:
            session.run("""
                MERGE (p:Project {project_id: $id})
                SET p.name = $name, p.status = $status
            """, id=proj["id"], name=proj["name"], status=proj["status"])

        # 4. Sync Sessions
        for s in sessions:
            cypher = """
            MERGE (s:Session {session_id: $sid})
            SET s.started_at = $start,
                s.ended_at = $end,
                s.status = $status,
                s.exit_summary = $summary,
                s.operator = $op
            """
            session.run(cypher, 
                sid=s["session_id"], 
                start=s["timestamp_start"],
                end=s["timestamp_end"],
                status=s["state"],
                summary=s.get("exit_summary", ""),
                op=s.get("operator", "user")
            )
            processed_nodes += 1
            
            # Link Session -> Focused Project
            focus = s.get("context", {}).get("focus_project")
            if focus:
                session.run("""
                    MATCH (s:Session {session_id: $sid})
                    MERGE (p:Project {project_id: $pid})
                    MERGE (s)-[r:FOCUSED_ON]->(p)
                    SET r.primary = true
                """, sid=s["session_id"], pid=focus)

        # 5. Sync Tasks
        for t in tasks:
            cypher = """
            MERGE (t:Task {task_id: $tid})
            SET t.description = $desc,
                t.status = $status,
                t.priority = $prio,
                t.created_at = $created,
                t.project_id = $pid
            """
            session.run(cypher,
                tid=t["task_id"],
                desc=t["description"],
                status=t["status"],
                prio=t.get("priority", "MEDIUM"),
                created=t["lifecycle"]["created_at"],
                pid=t["project"]
            )
            processed_nodes += 1

            # Link Task -> Project
            session.run("""
                MATCH (t:Task {task_id: $tid})
                MERGE (p:Project {project_id: $pid})
                MERGE (p)-[:HAS_TASK]->(t)
            """, tid=t["task_id"], pid=t["project"])
            processed_rels += 1

            # Link Task -> Session (Created In)
            created_in = t["lifecycle"].get("created_in_session")
            if created_in:
                session.run("""
                    MATCH (t:Task {task_id: $tid})
                    MATCH (s:Session {session_id: $sid})
                    MERGE (s)-[:CREATED_TASK]->(t)
                """, tid=t["task_id"], sid=created_in)
                processed_rels += 1
    
    driver.close()
    print(f"✅ Sync Complete. Processed {processed_nodes} nodes, {processed_rels} rels.")

if __name__ == "__main__":
    try:
        sync_graph()
    except Exception as e:
        print(f"❌ Sync Failed: {e}")
