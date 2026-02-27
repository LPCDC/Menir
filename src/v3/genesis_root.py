import logging
from src.v3.menir_bridge import MenirBridge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GenesisRoot")

def apply_root_ontology():
    bridge = MenirBridge()
    query = """
    // 1. The Core (Luiz)
    MERGE (luiz:Person:Root {name: 'Luiz', role: 'Owner'})
    
    // 2. Commercial Layer
    MERGE (liblabs:Company {name: 'LibLabs', type: 'Holding'})
    MERGE (tivoli:Company {name: 'Tivoli', type: 'Client'})
    MERGE (mau:Company {name: 'MAU', type: 'Venture'})
    MERGE (menir:System {name: 'Menir', version: '3.1'})
    
    // 3. Social Layer (Inner Circle)
    // Fix: Match by Name first to respect Constraint, then SET properties
    MERGE (debora:Person {name: 'Débora Vezzoli'})
    SET debora.role = 'Author', debora.context = 'Real World'
    
    MERGE (newton:Person {name: 'Newton'})
    SET newton.context = 'Real World'
    
    MERGE (caroline:Person {name: 'Caroline Moreira'})
    SET caroline.context = 'Real World'

    // 4. The Self (Metacognition) - Menir Self-Awareness
    MERGE (truth:Concept {name: 'Truth'})
    MERGE (memory:Concept {name: 'Memory'})
    MERGE (fiction:Concept {name: 'Fiction'})
    MERGE (menir)-[:UPHOLDS]->(truth)
    MERGE (menir)-[:PRESERVES]->(memory)
    MERGE (menir)-[:DISTINGUISHES {method: 'Root Ontology'}]->(fiction)
    MERGE (menir)-[:DEFINED_AS]->(desc:Description {text: 'Ontology-Driven Intelligence Engine'})
    MERGE (menir)-[:TARGETS_MARKET]->(mkt:Market {name: 'Enterprise Memory'})
    
    // 5. Relationships - Commercial
    MERGE (luiz)-[:OWNS]->(liblabs)
    MERGE (luiz)-[:OWNS]->(menir)
    MERGE (luiz)-[:MANAGES]->(tivoli)
    MERGE (liblabs)-[:PROVIDED_SERVICE]->(tivoli)
    MERGE (liblabs)-[:PARTNER_OF]->(mau)
    MERGE (menir)-[:MONITORS]->(tivoli)
    MERGE (caroline)-[:OWNS]->(mau)
    
    // 6. Relationships - Social
    MERGE (luiz)-[:FRIEND_OF]->(debora)
    MERGE (luiz)-[:FRIEND_OF]->(newton)
    MERGE (luiz)-[:EX_PARTNER_OF]->(caroline)
    """
    
    with bridge.driver.session() as session:
        session.run(query)
        logger.info("✅ Root Ontology Applied Successfully.")
        
    bridge.close()

if __name__ == "__main__":
    apply_root_ontology()
