import json
import os
from typing import Dict, Any, List
from neo4j import GraphDatabase
from dotenv import load_dotenv

import logging

# Setup Logger
logging.basicConfig(
    filename="menir_scribe.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

class ScribeApplicator:
    """
    Executes Scribe Proposals (JSON diffs) into Neo4j.
    Uses MERGE for idempotency.
    Persists PROVENANCE metadata.
    Logs actions to menir_scribe.log.
    """
    
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "menir123")
        db = os.getenv("NEO4J_DB", "neo4j")
        
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.db = db

    def apply_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply nodes and relationships from proposal.
        Returns report of changes.
        """
        stats = {"nodes_created": 0, "relationships_created": 0, "errors": []}
        
        # EXTRACT PROVENANCE
        source_meta = proposal.get("source", {})
        proposal_id = proposal.get("proposal_id", "unknown")
        
        provenance_props = {
            "source_file": source_meta.get("file", "unknown"),
            "source_project": source_meta.get("project", "unknown"),
            "source_timestamp": source_meta.get("timestamp", "unknown"),
            "proposal_id": proposal_id
        }
        
        with self.driver.session(database=self.db) as session:
            # 1. Apply Nodes with Provenance
            for node in proposal.get("nodes", []):
                try:
                    label = node.get("label")
                    props = node.get("properties", {})
                    
                    id_key = "id" if "id" in props else "name"
                    if id_key not in props:
                        stats["errors"].append(f"Node missing ID/Name: {node}")
                        continue
                    
                    # Merge provenance into properties
                    full_props = {**props, **provenance_props}

                    cypher = f"MERGE (n:{label} {{ {id_key}: $id }}) SET n += $props"
                    session.run(cypher, id=props[id_key], props=full_props)
                    stats["nodes_created"] += 1
                except Exception as e:
                    stats["errors"].append(f"Node Error: {e}")

            # 2. Apply Relationships
            for rel in proposal.get("relationships", []):
                try:
                    start_name = rel.get("start")
                    rel_type = rel.get("type")
                    end_name = rel.get("end")
                    
                    # Store minimal provenance on relationship too?
                    # For now, just create relationship.
                    cypher = f"""
                    MATCH (a), (b)
                    WHERE (a.name = $start OR a.id = $start) AND (b.name = $end OR b.id = $end)
                    MERGE (a)-[r:{rel_type}]->(b)
                    SET r.proposal_id = $pid
                    """
                    session.run(cypher, start=start_name, end=end_name, pid=proposal_id)
                    stats["relationships_created"] += 1
                except Exception as e:
                    stats["errors"].append(f"Rel Error: {e}")
        
        # Log Summary
        if stats["errors"]:
            logging.error(f"Proposal {proposal_id} applied with ERRORS. Stats: {stats}")
        else:
            logging.info(f"Proposal {proposal_id} applied SUCCESSFULLY. Stats: {stats}")
            
        return stats

    def close(self):
        self.driver.close()
