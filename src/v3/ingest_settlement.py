import logging
from src.v3.menir_bridge import MenirBridge
from src.v3.tenant_middleware import current_tenant_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IngestSettlement")

def ingest_settlement():
    bridge = MenirBridge()
    query = """
    // 1. Context setup
    MERGE (t:Tenant {id: 'root_admin'})
    
    // We expect these nodes to exist from previous ingestions
    MERGE (luiz:Person:Root {name: 'Luiz'})
    MERGE (caroline:Person {name: 'Caroline Moreira'})
    
    // Supplement identity data from the document
    SET luiz.cpf = '314.098.668-82', luiz.nationality = 'Brasileiro'
    SET caroline.cpf = '220.883.038-55', caroline.nationality = 'Brasileira'

    // 2. Temporal Tree (BFO/Time)
    MERGE (y2025:Year {value: 2025})
    MERGE (y2025m11:Month {value: 11})
    MERGE (y2025m11d11:Day {value: 11})
    MERGE (y2025)-[:HAS_MONTH]->(y2025m11)
    MERGE (y2025m11)-[:HAS_DAY]->(y2025m11d11)
    
    MERGE (y2026:Year {value: 2026})
    MERGE (y2026m01:Month {value: 1})
    MERGE (y2026m01d14:Day {value: 14})
    MERGE (y2026)-[:HAS_MONTH]->(y2026m01)
    MERGE (y2026m01)-[:HAS_DAY]->(y2026m01d14)

    MERGE (y2025)-[:BELONGS_TO]->(t)
    MERGE (y2025m11)-[:BELONGS_TO]->(t)
    MERGE (y2025m11d11)-[:BELONGS_TO]->(t)
    MERGE (y2026)-[:BELONGS_TO]->(t)
    MERGE (y2026m01)-[:BELONGS_TO]->(t)
    MERGE (y2026m01d14)-[:BELONGS_TO]->(t)

    // 3. Concepts (SKOS)
    MERGE (c_legal:Concept {name: 'Legal Agreement'})
    MERGE (c_finance:Concept {name: 'Financial Settlement'})
    MERGE (c_legal)-[:BELONGS_TO]->(t)
    MERGE (c_finance)-[:BELONGS_TO]->(t)

    // 4. Documents (PROV-O)
    MERGE (doc_debt:Document {name: 'Termo de Confissão/Quitação de Dívida'})
    SET doc_debt.type = 'Legal Contract', 
        doc_debt.subject = 'Quitação de dívida financeira e laborativa'
    MERGE (doc_debt)-[:Pertains_To]->(c_legal)
    MERGE (doc_debt)-[:Pertains_To]->(c_finance)
    MERGE (doc_debt)-[:BELONGS_TO]->(t)
    
    MERGE (doc_settlement:Document {name: 'Termo Simples de Quitação de Dívida'})
    SET doc_settlement.type = 'Legal Declaration',
        doc_settlement.location = 'Guarujá',
        doc_settlement.status = 'Irrevogável e Irretratável'
    MERGE (doc_settlement)-[:WAS_DERIVED_FROM]->(doc_debt)
    MERGE (doc_settlement)-[:Pertains_To]->(c_legal)
    MERGE (doc_settlement)-[:BELONGS_TO]->(t)

    // 5. Events (Continuants vs Occurrents)
    
    // Event 1: The original debt acknowledgment
    MERGE (ev_debt:Event {name: 'Assinatura Original de Dívida'})
    MERGE (ev_debt)-[:OCCURRED_ON]->(y2025m11d11)
    MERGE (luiz)-[:PARTICIPATED_IN {role: 'Devedor'}]->(ev_debt)
    MERGE (caroline)-[:PARTICIPATED_IN {role: 'Credora'}]->(ev_debt)
    MERGE (ev_debt)-[:PRODUCED]->(doc_debt)
    MERGE (ev_debt)-[:BELONGS_TO]->(t)

    // Event 2: The final settlement/quit
    MERGE (ev_settlement:Event {name: 'Quitação Integral de Dívida'})
    SET ev_settlement.total_transferred_brl = 34500.00,
        ev_settlement.total_labor_compensation_brl = 6104.32,
        ev_settlement.total_settled_brl = 40604.32,
        ev_settlement.condition = 'Inexistente qualquer dívida ou compromisso futuro'
    
    MERGE (ev_settlement)-[:OCCURRED_ON]->(y2026m01d14)
    MERGE (caroline)-[:PARTICIPATED_IN {role: 'Declarante/Credora Satisfeita'}]->(ev_settlement)
    MERGE (luiz)-[:PARTICIPATED_IN {role: 'Devedor Quitado'}]->(ev_settlement)
    MERGE (ev_settlement)-[:PRODUCED]->(doc_settlement)
    MERGE (ev_settlement)-[:RESOLVED]->(ev_debt)
    MERGE (ev_settlement)-[:BELONGS_TO]->(t)
    """
    
    with bridge.driver.session() as session:
        token = current_tenant_id.set("root_admin")
        try:
            session.run(query)
            logger.info("✅ Debt Settlement Document Ingested Successfully.")
        finally:
            current_tenant_id.reset(token)
            
    bridge.close()

if __name__ == "__main__":
    ingest_settlement()
