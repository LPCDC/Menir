from src.v3.menir_bridge import MenirBridge
import logging

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Cleaner")

bridge = MenirBridge()

clean_query = """
// 1. Delete Orphans (Nodes with no relationships)
// 1. Delete Orphans
MATCH (n) 
WHERE COUNT { (n)--() } = 0 
AND NOT n.name IN ['Débora Vezzoli', 'Menir', 'Tivoli', 'Luiz', 'Newton', 'Caroline Moreira', 'LibLabs', 'MAU', 'Default_Project'] 
DETACH DELETE n
"""

reset_narrative_query = """
// 2. Delete Narrative Nodes
MATCH (n)
WHERE NOT n.name IN ['Débora Vezzoli', 'Menir', 'Tivoli', 'Luiz', 'Newton', 'Caroline Moreira', 'LibLabs', 'MAU']
AND NOT n:Person:Root // Protect Root entities by Label too if applicable
AND NOT n.role = 'Author' // Extra safety for Débora
DETACH DELETE n
"""

# Just delete orphans first
orphan_fix = "MATCH (n) WHERE COUNT { (n)--() } = 0 AND NOT n.name IN ['Débora Vezzoli', 'Menir', 'Tivoli', 'Luiz', 'Newton', 'Caroline Moreira', 'LibLabs', 'MAU'] DETACH DELETE n"

try:
    with bridge.driver.session() as session:
        # 1. Clean Orphans
        r = session.run(orphan_fix)
        logger.info(f"Orphans Removed.")
        
        # 2. Verify 'Débora' exists, if not create her (The Anchor)
        check = session.run("MATCH (p:Person {name: 'Débora Vezzoli'}) RETURN count(p) as c").single()
        if check and check["c"] == 0:
            logger.info("Re-creating Anchor: Débora Vezzoli")
            session.run("CREATE (:Person {name: 'Débora Vezzoli', role: 'Author'})")
        else:
            logger.info("Anchor Verified: Débora Vezzoli matches.")

finally:
    bridge.close()
