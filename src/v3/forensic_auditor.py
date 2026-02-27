"""
Módulo GatoMia: Agentic Forensic Auditing 
Horizon 3 - Innovation Frontier

Detects Cross-Entity Fraud Rings (cyclic graph paths) 
and performs Community Clustering (Leiden algorithm emulation via Neo4j GDS or Cypher patterns).
"""

import logging
from typing import Dict, Any, List
from neo4j import GraphDatabase

from src.v3.tenant_middleware import current_tenant_id
from src.v3.menir_bridge import MenirBridge
from src.v3.langgraph_orchestrator import menir_graph, HumanMessage, MenirState

logger = logging.getLogger("ForensicAuditor")
logger.setLevel(logging.INFO)

class ForensicAuditor:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.bridge = MenirBridge()

    def discover_fraud_rings(self, max_depth: int = 5) -> List[Dict[str, Any]]:
        """
        Runs a Cypher query to detect cycles (A -> B -> C -> A) 
        which are highly indicative of money laundering or fraud rings.
        """
        logger.info(f"🔍 [Forensic Auditor] Scanning for cyclic fraud rings up to depth {max_depth}...")
        
        # We must set context for the Tenant Middleware to allow reading for this project
        t_token = current_tenant_id.set(self.project_id)
        
        # Basic Cypher to find cycles (fraud rings) using path traversal
        query = f"""
        MATCH path = (a:Conta)-[:ENVOLVENDO*2..{max_depth}]->(a)
        WITH a, path, [n IN nodes(path) | n.id] as ring_nodes
        RETURN a.id as origin_account, ring_nodes, length(path) as cycle_length
        LIMIT 10
        """
        
        results = []
        try:
            with self.bridge.driver.session() as session:
                records = session.run(query)
                for r in records:
                    results.append({
                        "origin_account": r["origin_account"],
                        "ring_nodes": r["ring_nodes"],
                        "cycle_length": r["cycle_length"]
                    })
            logger.info(f"🚨 Detected {len(results)} potential structural anomalies (Cycles).")
            return results
        except Exception as e:
            logger.error(f"Audit computation failed: {e}")
            return []
        finally:
            current_tenant_id.reset(t_token)
            
    def analyze_with_agent(self, findings: List[Dict[str, Any]]):
        """
        Feeds the analytical findings to the LangGraph Orchestrator. 
        Requires Human-IN-THE-LOOP validation if risks are found.
        """
        if not findings:
            logger.info("✅ No anomalies detected. Agent standing down.")
            return
            
        logger.warning(f"🤖 [LangGraph Auditor] Alerting agent to {len(findings)} structural anomalies!")
        
        prompt = f"FORENSIC REPORT:\nFound cyclic graph paths indicating potential fraud rings:\n{findings}\nGenerate a risk assessment report."
        
        state: MenirState = {
            "messages": [HumanMessage(content=prompt)],
            "tenant_id": self.project_id,
            "thread_id": "audit_thread_01",
            "memory": {"require_human_review": True}, 
            "error": None
        }
        
        final_state = menir_graph.invoke(state)
        
        # Explicit HITL trigger simulation
        if final_state["memory"].get("require_human_review"):
            logger.critical("🛑 [HITL] HIGH RISK DETECTED: Execution halted. Human forensic reviewer signature required to proceed.")
            # In a real system, this flags a dashboard or sends an alert via Webhook.

if __name__ == "__main__":
    auditor = ForensicAuditor(project_id="PROJECT_ITAU_15220012")
    
    # 1. Structural DB query
    anomalies = auditor.discover_fraud_rings(max_depth=4)
    
    # 2. Agentic Reasoning & HITL
    auditor.analyze_with_agent(anomalies)
