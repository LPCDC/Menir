
import os
import datetime
from typing import Dict, Any, List, Optional
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment
load_dotenv()

def get_driver():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "menir123")
    return GraphDatabase.driver(uri, auth=(user, password))

def query_tasks_graph(intent: str, **params) -> Dict[str, Any]:
    """
    Main entry point for Task GraphRAG.
    Executes a read-only intent against the System Graph.
    """
    driver = None
    try:
        driver = get_driver()
        with driver.session() as session:
            if intent == "PROJECT_OPEN_TASKS":
                return _project_open_tasks(session, params)
            elif intent == "PROJECT_SUMMARY":
                return _project_summary(session, params)
            elif intent == "LAST_SESSION_TASKS":
                return _last_session_tasks(session, params)
            elif intent == "STALE_TASKS":
                return _stale_tasks(session, params)
            else:
                return {"error": {"code": "INVALID_INTENT", "message": f"Unknown intent: {intent}"}}
    except Exception as e:
        return {"error": {"code": "EXECUTION_ERROR", "message": str(e)}}
    finally:
        if driver:
            driver.close()

# -------------------------------------------------------------------------
# Internal Cypher Implementations
# -------------------------------------------------------------------------

def _project_open_tasks(session, params) -> Dict:
    pid = params.get("project_id")
    if not pid:
        return {"error": {"code": "MISSING_PARAM", "message": "project_id is required"}}

    cypher = """
    MATCH (p:Project {project_id: $pid})-[:HAS_TASK]->(t:Task)
    WHERE t.status IN ['OPEN', 'IN_PROGRESS', 'BLOCKED']
    RETURN t, duration.inDays(datetime(t.created_at), datetime()).days as age
    ORDER BY age DESC
    """
    result = session.run(cypher, pid=pid)
    tasks = []
    for record in result:
        node = record["t"]
        tasks.append({
            "task_id": node["task_id"],
            "description": node["description"],
            "status": node["status"],
            "priority": node.get("priority", "MEDIUM"),
            "created_at": node["created_at"],
            "age_days": record["age"]
        })
    
    return {"project_id": pid, "open_tasks": tasks, "count": len(tasks)}

def _project_summary(session, params) -> Dict:
    pid = params.get("project_id")
    if not pid:
        return {"error": {"code": "MISSING_PARAM", "message": "project_id is required"}}

    # 1. Project Info + Stats
    stats_cypher = """
    MATCH (p:Project {project_id: $pid})
    OPTIONAL MATCH (p)-[:HAS_TASK]->(t:Task)
    RETURN p.name as name, p.status as status,
           sum(CASE WHEN t.status IN ['OPEN', 'IN_PROGRESS'] THEN 1 ELSE 0 END) as open_count,
           sum(CASE WHEN t.status = 'DONE' THEN 1 ELSE 0 END) as done_count,
           sum(CASE WHEN t.status = 'BLOCKED' THEN 1 ELSE 0 END) as blocked_count,
           max(CASE WHEN t.status = 'OPEN' THEN duration.inDays(datetime(t.created_at), datetime()).days ELSE 0 END) as oldest_open
    """
    stats = session.run(stats_cypher, pid=pid).single()
    
    if not stats:
        return {"error": {"code": "NOT_FOUND", "message": f"Project {pid} not found"}}

    # 2. Recent Activity (Sessions)
    activity_cypher = """
    MATCH (s:Session)-[:FOCUSED_ON]->(p:Project {project_id: $pid})
    RETURN s
    ORDER BY s.started_at DESC LIMIT 3
    """
    recent_sessions = [dict(row["s"]) for row in session.run(activity_cypher, pid=pid)]

    return {
        "project_info": {
            "project_id": pid,
            "name": stats["name"],
            "status": stats["status"]
        },
        "tasks_stats": {
            "open_count": stats["open_count"],
            "done_count": stats["done_count"],
            "blocked_count": stats["blocked_count"],
            "oldest_open_age_days": stats["oldest_open"]
        },
        "recent_activity": recent_sessions
    }

def _last_session_tasks(session, params) -> Dict:
    ref = params.get("session_ref", "last")
    
    if ref == "last":
        # Find last CLOSED session
        session_locator = """
        MATCH (s:Session)
        WHERE s.status = 'CLOSED'
        RETURN s ORDER BY s.ended_at DESC LIMIT 1
        """
    else:
        session_locator = """
        MATCH (s:Session {session_id: $sid}) RETURN s
        """
        
    s_rec = session.run(session_locator, sid=ref).single()
    if not s_rec:
        return {"error": {"code": "NOT_FOUND", "message": "Session not found"}}
    
    sess_node = s_rec["s"]
    sid = sess_node["session_id"]
    
    # Get Tasks created in this session
    tasks_cypher = """
    MATCH (s:Session {session_id: $sid})-[:CREATED_TASK]->(t:Task)
    RETURN t
    """
    tasks = [dict(row["t"]) for row in session.run(tasks_cypher, sid=sid)]
    
    return {
        "session": dict(sess_node),
        "tasks_created": tasks,
        "count": len(tasks)
    }

def _stale_tasks(session, params) -> Dict:
    min_age = params.get("min_age_days", 7)
    pid = params.get("project_id") # Optional filter
    
    where_clause = "WHERE t.status IN ['OPEN', 'IN_PROGRESS'] AND duration.inDays(datetime(t.created_at), datetime()).days >= $age"
    match_clause = "MATCH (t:Task)"
    
    if pid:
        match_clause = "MATCH (p:Project {project_id: $pid})-[:HAS_TASK]->(t:Task)"
        
    cypher = f"""
    {match_clause}
    {where_clause}
    RETURN t, duration.inDays(datetime(t.created_at), datetime()).days as age
    ORDER BY age DESC
    """
    
    result = session.run(cypher, age=min_age, pid=pid)
    stale_items = []
    for record in result:
        node = dict(record["t"])
        node["age_days"] = record["age"]
        stale_items.append(node)
        
    return {
        "criteria": {"min_age_days": min_age, "project_filter": pid},
        "stale_tasks": stale_items,
        "count": len(stale_items)
    }
