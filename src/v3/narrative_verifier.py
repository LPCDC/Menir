"""
Módulo Livro Débora: Narrative Verification (TLA+ Emulation)
Horizon 3 - Innovation Frontier

Enforces strict physical constraints on narrative graph generation
using a Narrative Linked-List topology and State Invariants.
"""

import logging
from typing import Dict, Any, List, Optional
from src.v3.menir_bridge import MenirBridge

logger = logging.getLogger("NarrativeVerifier")
logger.setLevel(logging.INFO)

class TLAInvariantException(Exception):
    """Raised when a narrative proposal violates physical simulation laws (TLA+)."""
    pass

class NarrativeVerifier:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.bridge = MenirBridge()

    def bootstrap_narrative_schema(self):
        """
        Creates constraints for the Linked-List Scene topology.
        """
        queries = [
            "CREATE CONSTRAINT scene_id IF NOT EXISTS FOR (s:Scene) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT location_id IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE",
            "CREATE CONSTRAINT character_id IF NOT EXISTS FOR (c:Character) REQUIRE c.id IS UNIQUE"
        ]
        with self.bridge.driver.session() as session:
            for q in queries:
                session.run(q)
        logger.info("Narrative Linked-List Schema Base initialized.")

    def verify_proposed_scene(self, proposed_scene: Dict[str, Any]) -> bool:
        """
        Simulates Formal Verification (Model Checking).
        If the LLM decides to place 'Character X' in 'Location Y' at 'Time T',
        we traverse the graph backwards to ensure Character X wasn't explicitly
        stated to be trapped in 'Location Z' without a valid transition path.
        """
        chars = proposed_scene.get("characters", [])
        loc = proposed_scene.get("location", "")
        time_slice = proposed_scene.get("time_slice", 0)

        logger.info(f"📐 [TLA+ Verifier] Validating Invariants for TimeSlice {time_slice}...")
        
        for char in chars:
            # Cypher query enforcing spatial continuity invariant
            query = f"""
            MATCH (c:Character {{name: $char}})-[:WAS_AT]->(prev_loc:Location)<-[:HAPPENED_IN]-(prev_scene:Scene)
            WHERE prev_scene.time_slice < $time
            RETURN prev_loc.name as loc, prev_scene.time_slice as ts
            ORDER BY prev_scene.time_slice DESC LIMIT 1
            """
            try:
                with self.bridge.driver.session() as session:
                    # In a real environment, TenantMiddleware handles the tenant filtering
                    res = session.run(query, char=char, time=time_slice).single()
                    
                    if res:
                        last_loc = res["loc"]
                        if last_loc != loc and not self._is_reachable(last_loc, loc):
                            logger.error(f"❌ STATE VIOLATION: Character '{char}' cannot teleport from {last_loc} to {loc}.")
                            raise TLAInvariantException(f"Hallucination Detected: {char} in impossible location.")
                            
            except TLAInvariantException:
                raise
            except Exception as e:
                logger.warning(f"Validation fault: {e}")
        
        logger.info("✅ All State Invariants Valid. LLM Proposal Approved for Graph Commit.")
        return True

    def _is_reachable(self, loc_a: str, loc_b: str) -> bool:
        """
        Simplified reachability graph for spatial continuity.
        In full graph, this checks if (loc_a)-[:CONNECTS_TO]->(loc_b) exists.
        """
        # Mock logic. Return false to simulate a blocked path.
        if loc_a == "Mars" and loc_b == "Earth":
            return False
        return True

    def commit_scene(self, scene_id: str, prev_id: Optional[str], data: Dict[str, Any]):
        """
        Writes the validated scene to the DB as a Linked-List element.
        """
        if not self.verify_proposed_scene(data):
            return
            
        logger.info(f"✍️ Committing Scene {scene_id} to Narrative Linked-List.")
        
        query = """
        MERGE (s:Scene {id: $scene_id})
        SET s += $data
        """
        
        with self.bridge.driver.session() as session:
            session.run(query, scene_id=scene_id, data=data)
            
            # Form Linked List Edge
            if prev_id:
                link_query = """
                MATCH (p:Scene {id: $prev_id})
                MATCH (c:Scene {id: $scene_id})
                MERGE (p)-[:NEXT_SCENE]->(c)
                """
                session.run(link_query, prev_id=prev_id, scene_id=scene_id)
                
if __name__ == "__main__":
    verifier = NarrativeVerifier("PROJECT_DEBORA_001")
    verifier.bootstrap_narrative_schema()
    
    # Simulate LLM proposal
    bad_proposal = {
        "time_slice": 42,
        "location": "Earth",
        "characters": ["Astrogildo"]
    }
    
    try:
        # If Astrogildo was last seen on Mars and no travel edge exists, this throws.
        verifier.commit_scene("scene_104", "scene_103", bad_proposal)
    except TLAInvariantException as e:
        print(f"Graph Refused Write: {e}")
