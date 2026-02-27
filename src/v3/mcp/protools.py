"""
Menir MCP Professional Tools
Implements the core observational capabilities for the Agent.
"""
import os
import json
import logging
import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
import mcp.types
from src.v3.graph_schema import STRICT_SCHEMA
from src.v3.menir_bridge import MenirBridge
from src.v3.mcp.security import PiiFilter

# Initialize Helper Logger
logger = logging.getLogger("MenirMCPTools")

# ==========================================
# Tool Logic
# ==========================================

class MenirTools:
    def __init__(self):
        # We initialize Bridge lazily or per-request to avoid keeping connections open?
        # Better to have a singleton bridge for the Server process.
        pass

    @staticmethod
    async def get_strict_schema() -> dict:
        """Returns the official Graph Schema for Menir."""
        return STRICT_SCHEMA

    @staticmethod
    async def search_logs(limit: int = 100, keyword: str = None) -> List[str]:
        """
        Reads the last N lines of menir.log.
        Applies horizontal truncation (>500 chars) and PII redaction.
        """
        log_path = os.path.join(os.getcwd(), 'logs', 'menir.log')
        if not os.path.exists(log_path):
             return ["Log file not found."]

        results = []
        try:
            # Efficient tailing for large files is complex in pure Python without deps,
            # but usually reading lines and taking last N is fine for <100MB logs.
            with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                
            # Filter first
            if keyword:
                lines = [l for l in lines if keyword.lower() in l.lower()]
            
            # Slice last N
            last_lines = lines[-limit:]
            
            for line in last_lines:
                # 1. PII Redaction
                clean_line = PiiFilter.redact_log_line(line)
                
                # 2. Horizontal Truncation
                if len(clean_line) > 500:
                    clean_line = clean_line[:500] + "...[TRUNCATED]"
                
                results.append(clean_line.strip())
                
            return results
        except Exception as e:
            return [f"Error reading logs: {str(e)}"]

    @staticmethod
    async def explain_node(uuid: str, show_pii: bool = False) -> dict:
        """
        Fetches Node properties + 1-Hop Relationships with 5s Timeout.
        """
        bridge = MenirBridge() # Assuming Env Vars are set
        try:
            # Enforce 5s Timeout on Neo4j Operation
            async def _fetch():
                # Note: MenirBridge is sync, so we wrap it or use it directly.
                # Since we are in an async function, we can run it in an executor if needed,
                # but for simplicity we rely on the bridge's internal speed.
                # However, to strictly enforce timeout at Python level:
                return await asyncio.to_thread(_get_node_data, bridge, uuid)

            data = await asyncio.wait_for(_fetch(), timeout=5.0)
            
            # Redact PII
            if not show_pii:
                data['properties'] = PiiFilter.redact_node(data.get('properties', {}))
                
            return data

        except asyncio.TimeoutError:
            return {"error": "Database timeout (5s)", "status": "offline"}
        except Exception as e:
             return {"error": f"Database Error: {str(e)}", "status": "error"}
        finally:
            bridge.close()

    @staticmethod
    async def check_quarantine_reasons(days: int = 7) -> List[dict]:
        """
        Analyzes nodes in 'quarantine' status.
        """
        bridge = MenirBridge()
        query = """
        MATCH (n:Document {status: 'quarantine'})
        WHERE n.ingested_at >= datetime() - duration({days: $days})
        RETURN n.filename as file, n.sha256 as hash, n.error_msg as error
        LIMIT 50
        """
        try:
            async def _run_query():
                 with bridge.driver.session() as session:
                     result = session.run(query, days=days)
                     return [{"file": r["file"], "hash": r["hash"], "error": r.get("error", "Unknown")} for r in result]

            return await asyncio.wait_for(_run_query(), timeout=5.0)

        except asyncio.TimeoutError:
             return [{"error": "Database timeout checking quarantine"}]
        except Exception as e:
             return [{"error": str(e)}]
        finally:
            bridge.close()

# Internal Helper for Explain Node
def _get_node_data(bridge, uuid):
    with bridge.driver.session() as session:
        # 1. Fetch Node
        node_q = "MATCH (n {uid: $uid}) RETURN labels(n) as labels, properties(n) as props"
        node_res = session.run(node_q, uid=uuid).single()
        
        if not node_res:
            return {"error": "Node not found"}
            
        # 2. Fetch 1-Hop Rels (Incoming & Outgoing)
        # Limit to 20 rels to avoid massive dumps
        rel_q = """
        MATCH (n {uid: $uid})-[r]-(target)
        RETURN type(r) as type, startNode(r) = n as is_start, labels(target) as other_labels, target.name as other_name, target.uid as other_uid
        LIMIT 20
        """
        rel_res = session.run(rel_q, uid=uuid)
        
        relationships = []
        for r in rel_res:
            direction = "OUT" if r["is_start"] else "IN"
            relationships.append({
                "type": r["type"],
                "direction": direction,
                "target_label": r["other_labels"][0] if r["other_labels"] else "Unknown",
                "target_name": r["other_name"] or "Unnamed",
                "target_uid": r["other_uid"]
            })
            
        return {
            "uid": uuid,
            "labels": node_res["labels"],
            "properties": node_res["props"],
            "relationships": relationships
        }
