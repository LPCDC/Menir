import os
import shutil
import logging
from src.v3.menir_bridge import MenirBridge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Rebuilder")

def nuke_and_genesis():
    bridge = MenirBridge()
    with bridge.driver.session() as session:
        # 1. NUKE
        logger.warning("☢️ NUKING DATABASE...")
        session.run("MATCH (n) DETACH DELETE n")
        
        # 2. DROP CONSTRAINTS (Optional, but clean)
        # Keeping them is actually better for integrity, skipping drop.

        # 3. GENESIS
        logger.info("🌱 EXECUTING GENESIS PROTOCOL...")
        session.run("""
            CREATE (p:Person:Root {name: 'Débora Vezzoli', role: 'Author', trust_level: 'GOLD'})
            CREATE (s:System {name: 'Menir', version: '3.1'})
            CREATE (o:Organization {name: 'Tivoli'})
            CREATE (s)-[:MONITORS]->(p)
            CREATE (p)-[:OWNS]->(o)
        """)
        logger.info("✅ GENESIS COMPLETE.")
    bridge.close()

def reset_files():
    # Move files from Archive back to Inbox
    base = "Menir_Inbox"
    archive = os.path.join(base, "Archive")
    
    # Files to look for (Partial match is safer)
    targets = ["Better in Manhattan"]
    
    if not os.path.exists(archive):
         logger.warning("No Archive folder found!")
         return

    count = 0
    for f in os.listdir(archive):
        if any(t in f for t in targets) and f.endswith(".pdf"):
            src = os.path.join(archive, f)
            dst = os.path.join(base, f)
            shutil.move(src, dst)
            logger.info(f"↺ RESET: {f} -> Inbox")
            count += 1
            
    if count == 0:
        logger.warning("No target PDF files found in Archive to reset!")

if __name__ == "__main__":
    nuke_and_genesis()
    reset_files()
