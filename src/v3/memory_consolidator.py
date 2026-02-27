"""
Menir Episodic Memory Consolidator
Horizon 4 - "NEVER Forgetting"

Periodically reads all active Threads from LangGraph 
and extracts psychological or architectural facts about the user.
Merges these facts as permanent `(:Memory)` nodes into the Neo4j Graph.
"""

import uuid
import logging
from typing import List, Dict
from src.v3.menir_bridge import MenirBridge

logger = logging.getLogger("MemoryConsolidator")
logger.setLevel(logging.INFO)

class EpisodicMemoryAgent:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.bridge = MenirBridge()

    def consolidate_recent_threads(self, mock_interactions: List[Dict[str, str]]):
        """
        Usually we'd read this from LangGraph's SqliteSaver checkpoints.
        For this implementation, we take a mocked list of chat strings.
        """
        logger.info(f"🧠 [Consolidator] Scanning {len(mock_interactions)} interactions for durable facts...")
        
        extracted_facts = []
        for i in mock_interactions:
            # LLM "Extract Fact" heuristic simulated below:
            if "i prefer" in i["content"].lower() or "always" in i["content"].lower():
                fact = f"User Preference: {i['content']}"
                extracted_facts.append(fact)
                
        if not extracted_facts:
            logger.info("No durable facts found in recent threads.")
            return

        self._commit_memories_to_graph(extracted_facts)

    def _commit_memories_to_graph(self, facts: List[str]):
        logger.info(f"✍️ [Memory Writer] Burning {len(facts)} facts into Long-Term Graph Memory.")
        
        query = """
        UNWIND $facts as fact
        MERGE (mem:Memory {content: fact, tenant_id: $tenant_id})
        ON CREATE SET mem.id = apoc.create.uuid(), mem.created_at = datetime()
        WITH mem
        MATCH (u:User {tenant_id: $tenant_id})
        MERGE (u)-[r:REMEMBERS]->(mem)
        ON CREATE SET r.strength = 1.0
        ON MATCH SET r.strength = CASE WHEN r.strength < 5.0 THEN r.strength + 0.1 ELSE r.strength END
        RETURN mem.content, r.strength
        """
        
        try:
            with self.bridge.driver.session() as session:
                # Ensure User exists first
                session.run("MERGE (u:User {tenant_id: $tenant_id}) ON CREATE SET u.name = 'Architect'")
                
                # Write Memories
                records = session.run(query, facts=facts, tenant_id=self.tenant_id)
                for r in records:
                    logger.info(f"💾 Permanently Stored: '{r['mem.content']}' (Strength: {r['r.strength']})")
                    
        except Exception as e:
            logger.error(f"Failed to burn episodic memory: {e}")

if __name__ == "__main__":
    agent = EpisodicMemoryAgent("CORE_USER_001")
    
    # Simulate a daily cron job picking up chats
    threads = [
        {"role": "user", "content": "I prefer using dark mode to preserve my retinas."},
        {"role": "user", "content": "Always validate the SHACL models before hitting the prefeitura endpoint."},
        {"role": "user", "content": "Did you see that football match?"} # Doesn't trigger the heuristic
    ]
    
    agent.consolidate_recent_threads(threads)
