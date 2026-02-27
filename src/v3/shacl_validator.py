"""
Módulo Otani: Agnostic BIM SHACL Validator
Horizon 3 - Innovation Frontier

Transpiles building codes into native Neo4j spatial graph queries.
Provides mathematically rigorous constraint checking without locking into
proprietary IFC/Revit parsers directly.
"""

import logging
from typing import Dict, Any, List
from src.v3.menir_bridge import MenirBridge

logger = logging.getLogger("SHACLValidator")
logger.setLevel(logging.INFO)

class SHACLComplianceError(Exception):
    pass

class RulebookOtani:
    """
    Simulates RDF/SHACL rules natively in Cypher.
    Example: 'Rotas de Fuga' (Exit Routes) in NBR 9050 / Código de Obras.
    """
    
    @staticmethod
    def get_corridor_width_rule() -> str:
        """
        SHACL translation: Shape Node `Corredor`, Property `width` >= 1.20 meters.
        """
        return """
        MATCH (c:Corridor)
        WHERE c.width < 1.20
        RETURN c.id as violation_node, c.width as current_width, 'MIN_WIDTH_1_20' as rule
        """
        
    @staticmethod
    def get_maximum_exit_distance_rule(max_meters: float = 35.0) -> str:
        """
        SHACL translation: All `Room` nodes must have a path to an `Exit` 
        where the sum of link distances is <= 35m.
        """
        return f"""
        MATCH p = (r:Room)-[:CONNECTS_TO*1..10]->(e:Exit)
        WITH r, [rel IN relationships(p) | rel.distance] AS distances
        WITH r, reduce(s = 0, d IN distances | s + d) as total_dist
        WHERE total_dist > {max_meters}
        RETURN r.id as violation_node, total_dist as current_dist, 'MAX_EXIT_DIST_{max_meters}' as rule
        """


class BIMValidator:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.bridge = MenirBridge()

    def load_agnostic_geometry(self, space_nodes: List[Dict[str, Any]]):
        """
        Ingests decoupled spatial nodes: Room, Corridor, Door, Exit.
        """
        logger.info(f"🏗️ [BIM Validator] Ingesting {len(space_nodes)} agnostic spatial nodes.")
        query = """
        UNWIND $batch as row
        MERGE (s:Space {id: row.id})
        SET s += row
        WITH s, row
        CALL apoc.create.addLabels(s, [row.type]) YIELD node
        RETURN node
        """
        with self.bridge.driver.session() as session:
            session.run(query, batch=space_nodes)

    def validate_building_codes(self) -> List[Dict[str, Any]]:
        """
        Executes the SHACL/Cypher rulebook against the graph.
        Returns a list of compliance violations.
        """
        logger.info("📐 [Otani Engine] Assessing Compliance Constraints (SHACL Sandbox)...")
        
        violations = []
        rules = [
            RulebookOtani.get_corridor_width_rule(),
            RulebookOtani.get_maximum_exit_distance_rule()
        ]
        
        try:
            with self.bridge.driver.session() as session:
                for idx, rule_cypher in enumerate(rules):
                    logger.debug(f"Evaluating Rule #{idx+1}...")
                    res = session.run(rule_cypher)
                    for r in res:
                        violations.append({
                            "node": r["violation_node"],
                            "measurement": r.get("current_width") or r.get("current_dist"),
                            "broken_rule": r["rule"]
                        })
                        
            if violations:
                logger.error(f"❌ COMPLIANCE FAILED: Found {len(violations)} spatial violations.")
                for v in violations:
                    logger.warning(f"  -> Node {v['node']} broke rule {v['broken_rule']} ({v['measurement']})")
                return violations
            else:
                logger.info("✅ COMPLIANCE PASSED: All building geometries satisfy the active rulebook.")
                return []
                
        except Exception as e:
            logger.error(f"Validation Engine Exception: {e}")
            raise SHACLComplianceError("Engine fault during validation.")


if __name__ == "__main__":
    validator = BIMValidator("PROJECT_OTANI_003")
    
    # Mocking Agnostic BIM data
    mock_spaces = [
        {"id": "c_alpha", "type": "Corridor", "width": 1.05}, # Violation: < 1.20
        {"id": "r_beta", "type": "Room", "area": 30.5}
    ]
    
    validator.load_agnostic_geometry(mock_spaces)
    results = validator.validate_building_codes()
    if results:
        print("Project requires architectural revisions before municipal submission.")
