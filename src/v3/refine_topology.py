import logging
from src.v3.menir_bridge import MenirBridge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Refiner")

def refine_graph():
    bridge = MenirBridge()
    with bridge.driver.session() as session:
        # 1. Kill Zombie Tivoli
        logger.info("🔪 Removing Zombie Tivoli (Organization)...")
        res = session.run("MATCH (o:Organization {name: 'Tivoli'}) DETACH DELETE o RETURN count(o) as c")
        c = res.single()['c']
        logger.info(f"   Deleted {c} Zombie Node(s).")
        
        # 2. Stop Menir Spying on People
        logger.info("✂️  Cutting Illegal Surveillance (Menir->Person)...")
        res = session.run("MATCH (:System {name: 'Menir'})-[r:MONITORS]->(:Person) DELETE r RETURN count(r) as c")
        c = res.single()['c']
        logger.info(f"   Severed {c} Bad Link(s).")
        
        logger.info("✅ Refinement Complete.")
        
    bridge.close()

if __name__ == "__main__":
    refine_graph()
