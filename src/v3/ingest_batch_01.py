import logging
from src.v3.menir_bridge import MenirBridge
from src.v3.tenant_middleware import current_tenant_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IngestBatch01")

def ingest_batch_01():
    bridge = MenirBridge()
    query = """
    // 1. Root & Tenant Context
    MERGE (luiz:Person:Root {name: 'Luiz'})
    MERGE (t:Tenant {id: 'root_admin'})
    
    // 2. Architectural Timeline & Events (BFO & Temporal)
    MERGE (y2025:Year {value: 2025}) // Assumed timeframe for V3 transition
    MERGE (y2025)-[:BELONGS_TO]->(t)
    
    MERGE (ev_v3:Event {name: 'Transição para a V3'})
    SET ev_v3.description = 'Substituição de bancos vetoriais isolados por um Knowledge Graph nativo no Neo4j.'
    MERGE (ev_v3)-[:OCCURRED_IN]->(y2025)
    MERGE (luiz)-[:PARTICIPATED_IN {role: 'Architect'}]->(ev_v3)
    MERGE (ev_v3)-[:BELONGS_TO]->(t)

    // 3. Document Provenance (PROV-O)
    MERGE (doc_kernel:Document {name: 'MENIR_KERNEL.xml'})
    SET doc_kernel.type = 'Manifesto', doc_kernel.description = 'Fundação do Motor Epistemológico'
    MERGE (doc_kernel)-[:WAS_DERIVED_FROM]->(ev_v3)
    MERGE (doc_kernel)-[:WAS_ATTRIBUTED_TO]->(luiz)
    MERGE (doc_kernel)-[:BELONGS_TO]->(t)
    
    // 4. Ideological Concepts (SKOS)
    MERGE (c_kg:Concept {name: 'Knowledge Graph'})
    MERGE (c_em:Concept {name: 'Enterprise Memory'})
    MERGE (c_kg)-[:BROADER]->(c_em)
    MERGE (ev_v3)-[:IMPLEMENTED]->(c_kg)
    MERGE (c_kg)-[:BELONGS_TO]->(t)
    MERGE (c_em)-[:BELONGS_TO]->(t)

    MERGE (c_axiom:Concept {name: 'Axioms'})
    MERGE (c_def:Concept {name: 'DEFAULT_MENIR'})
    MERGE (c_pep:Concept {name: 'PEPOSO_OVERRIDE'})
    
    MERGE (c_def)-[:NARROWER]->(doc_kernel)
    MERGE (c_pep)-[:NARROWER]->(doc_kernel)
    MERGE (c_axiom)-[:NARROWER]->(doc_kernel)
    
    MERGE (c_def)-[:BELONGS_TO]->(t)
    MERGE (c_pep)-[:BELONGS_TO]->(t)
    MERGE (c_axiom)-[:BELONGS_TO]->(t)

    // 5. Companies & Initiatives
    MERGE (liblabs:Company {name: 'LibLabs'})
    MERGE (mau:Company {name: 'MAU', type: 'Venture'})
    
    MERGE (luiz)-[:OWNS]->(liblabs)
    MERGE (liblabs)-[:PARTNER_OF]->(mau)
    
    MERGE (liblabs)-[:BELONGS_TO]->(t)
    MERGE (mau)-[:BELONGS_TO]->(t)

    // 6. Social Graph
    MERGE (debora:Person {name: 'Débora Vezzoli'})
    MERGE (newton:Person {name: 'Newton'})
    MERGE (caroline:Person {name: 'Caroline Moreira'})
    
    // 7. Contextual Interactions
    MERGE (c_fiction:Concept {name: 'Ficção'})
    MERGE (c_real:Concept {name: 'Realidade'})
    MERGE (c_fiction)-[:BELONGS_TO]->(t)
    MERGE (c_real)-[:BELONGS_TO]->(t)

    // Débora
    MERGE (ev_debora:Event {name: 'Colaboração Criativa'})
    MERGE (ev_debora)-[:OCCURRED_IN_CONTEXT]->(c_fiction)
    MERGE (luiz)-[:INTERACTED_WITH]->(ev_debora)
    MERGE (debora)-[:INTERACTED_WITH]->(ev_debora)
    
    // Newton
    MERGE (ev_newton:Event {name: 'Debates Filosóficos'})
    MERGE (ev_newton)-[:OCCURRED_IN_CONTEXT]->(c_real)
    MERGE (luiz)-[:INTERACTED_WITH]->(ev_newton)
    MERGE (newton)-[:INTERACTED_WITH]->(ev_newton)
    
    // Caroline
    MERGE (luiz)-[:EX_PARTNER_OF]->(caroline)
    MERGE (ev_caroline:Event {name: 'Desenvolvimento MAU'})
    MERGE (caroline)-[:OWNS]->(mau)
    MERGE (luiz)-[:PARTICIPATED_IN {role: 'Partner'}]->(ev_caroline)
    MERGE (caroline)-[:PARTICIPATED_IN {role: 'Lead'}]->(ev_caroline)
    MERGE (ev_caroline)-[:FOCUSED_ON]->(mau)

    MERGE (debora)-[:BELONGS_TO]->(t)
    MERGE (newton)-[:BELONGS_TO]->(t)
    MERGE (caroline)-[:BELONGS_TO]->(t)
    MERGE (ev_debora)-[:BELONGS_TO]->(t)
    MERGE (ev_newton)-[:BELONGS_TO]->(t)
    MERGE (ev_caroline)-[:BELONGS_TO]->(t)
    """
    
    with bridge.driver.session() as session:
        # Secure the execution with the admin tenant token
        token = current_tenant_id.set("root_admin")
        try:
            session.run(query)
            logger.info("✅ Core Architecture & Social Graph Ingested Successfully.")
        finally:
            current_tenant_id.reset(token)
            
    bridge.close()

if __name__ == "__main__":
    ingest_batch_01()
