import logging
from src.v3.menir_bridge import MenirBridge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OntologyRepair")

def repair_ontology():
    bridge = MenirBridge()
    session = bridge.driver.session()
    
    try:
        logger.info("🔧 PHASE 1: RESTORING ROOT REALITY...")
        # 1. Ensure Root Nodes exist
        session.run("""
            MERGE (l:Person:Root {name: 'Luiz'}) SET l.role = 'Owner'
            MERGE (lib:Company {name: 'LibLabs'}) 
            MERGE (menir:System {name: 'Menir'}) 
            MERGE (tivoli:Company {name: 'Tivoli'}) 
            MERGE (mau:Company {name: 'MAU'})
            
            MERGE (deb:Person {name: 'Débora Vezzoli'}) SET deb.context = 'Real World'
            MERGE (newt:Person {name: 'Newton'}) SET newt.context = 'Real World'
            MERGE (carol:Person {name: 'Caroline Moreira'}) SET carol.context = 'Real World'
            
            // Re-establish Root Valid Connections
            MERGE (l)-[:OWNS]->(lib)
            MERGE (l)-[:OWNS]->(menir)
            MERGE (l)-[:MANAGES]->(tivoli)
            MERGE (lib)-[:PROVIDED_SERVICE]->(tivoli)
            MERGE (menir)-[:MONITORS]->(tivoli)
            
            MERGE (l)-[:FRIEND_OF]->(deb)
            MERGE (l)-[:FRIEND_OF]->(newt)
            MERGE (l)-[:EX_PARTNER_OF]->(carol)
            MERGE (carol)-[:OWNS]->(mau)
            MERGE (lib)-[:PARTNER_OF]->(mau)
        """)
        
        logger.info("📚 PHASE 2: ANCHORING FICTION...")
        # 2. Link Author to Document
        session.run("""
            MATCH (deb:Person {name: 'Débora Vezzoli'})
            MATCH (doc:Document) WHERE doc.filename CONTAINS 'Better in Manhattan'
            MERGE (deb)-[:WROTE]->(doc)
        """)
        
        logger.info("🚧 PHASE 3: ISOLATING CHARACTERS...")
        # 3. Ensure Characters connect to Document and NOT Reality
        fictional_names = ["Spencer", "Caroline Howell", "Joe", "Lauren", "Andrew"]
        
        session.run("""
            MATCH (c:Person) WHERE c.name IN $names
            MATCH (doc:Document) WHERE doc.filename CONTAINS 'Better in Manhattan'
            MERGE (c)-[:MENTIONED_IN]->(doc)
        """, names=fictional_names)
        
        # 4. PURGE Contamination (Delete links from Fiction to Reality)
        # Assuming Reality nodes are the ones we defined in Phase 1
        purge_query = """
            MATCH (fic:Person) WHERE fic.name IN $names
            MATCH (fic)-[r]-(real)
            WHERE real.name IN ['Luiz', 'LibLabs', 'Menir', 'Tivoli', 'MAU', 'Newton', 'Caroline Moreira']
            DELETE r
            RETURN count(r) as severed
        """
        result = session.run(purge_query, names=fictional_names).single()
        severed = result['severed'] if result else 0
        if severed > 0:
            logger.warning(f"⚠️ SEVERED {severed} ILLEGAL CONNECTIONS between Fiction and Reality.")

        logger.info("✨ PHASE 4: CAROLINE DISAMBIGUATION...")
        # Ensure they are distinct
        check_carol = session.run("""
            MATCH (c1:Person {name: 'Caroline Moreira'}), (c2:Person {name: 'Caroline Howell'})
            RETURN elementId(c1) <> elementId(c2) as distinct_persons
        """).single()
        
        if check_carol and check_carol['distinct_persons']:
             logger.info("✅ Caroline Moreira and Caroline Howell are DISTINCT entities.")
        else:
             logger.warning("⚠️ Warning: Could not verify Caroline distinction (maybe one node missing?).")

        logger.info("✅ ONTOLOGY ENFORCEMENT COMPLETE.")

    except Exception as e:
        logger.error(f"Repair Failed: {e}")
    finally:
        session.close()
        bridge.close()

if __name__ == "__main__":
    repair_ontology()
