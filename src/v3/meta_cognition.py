"""
Menir Core V5.1 - Meta Cognition Layer
Stores, manages, and queries the system's own architectural topology 
and the strict temporal Tax Ontology for Swiss ERP Integrations (Crésus).
"""
import logging
from neo4j import GraphDatabase, exceptions
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
from cachetools import cached, TTLCache

logger = logging.getLogger("MetaCognition")

class MenirOntologyManager:
    """
    Manages the architectural blueprint and temporal fiscal rules 
    directly within the Neo4j instance to ensure the Oracles remain 
    grounded physically and temporally.
    """
    def __init__(self, uri: str, auth: tuple):
        self.driver = GraphDatabase.driver(
            uri, 
            auth=auth,
            max_connection_pool_size=50,
            connection_acquisition_timeout=60.0    
        )
        
    def close(self):
        self.driver.close()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((exceptions.ServiceUnavailable, exceptions.TransientError, exceptions.SessionExpired)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def bootstrap_system_graph(self):
        """
        Injects the immutable Base Ontology and specific BECO ERP logic.
        Uses pure Cypher to guarantee schema rigidity and temporal constraints.
        """
        logger.info("Initializing Meta-Cognition: Bootstrapping System Ontology...")
        
        query = """
        // 1. A Arquitetura Fundacional
        MERGE (dev:Developer {name: "Luiz Oak", role: "Arquiteto Chefe"})
        MERGE (core:Core {name: "Menir", version: "5.1", engine: "Metacognitive Oracle"})
        MERGE (dev)-[:ARCHITECTED]->(core)

        // 2. O Tenant BECO e as Leis Suiças (Temporalidade Ativa - Crésus ERP)
        MERGE (tenant:Tenant {name: "BECO", target_erp: "Crésus"})
        MERGE (core)-[:SERVES_TENANT]->(tenant)
        
        // Criando as regras macro da AFC Suiça (Administração Federal das Contribuições)
        MERGE (rule_tdfn:TaxRule {name: "TDFN_Framework", authority: "ESTV/AFC"})
        MERGE (rule_effective:TaxRule {name: "TVA_Effective", authority: "ESTV/AFC"})
        
        // Arestas TEMPORAIS (Conectando a BECO às regras com validades de datas)
        MERGE (tenant)-[rt:ENFORCES_TAX_POLICY]->(rule_tdfn)
        SET rt.valid_from = "2024-01-01", 
            rt.valid_to = "2099-12-31", 
            rt.default_eur_chf_rate = 0.912
            
        MERGE (tenant)-[rt_tva:ENFORCES_TAX_POLICY]->(rule_effective)
        SET rt_tva.valid_from = "2024-01-01", 
            rt_tva.valid_to = "2099-12-31",
            rt_tva.standard_rate = 8.1,
            rt_tva.reduced_rate = 2.6,
            rt_tva.special_rate = 3.8

        RETURN core.name, tenant.name
        """
        with self.driver.session() as session:
            session.run(query)
            logger.info("✅ Core Ontology & Swiss Tax Rules (Temporal) successfully injected into the Graph.")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((exceptions.ServiceUnavailable, exceptions.TransientError, exceptions.SessionExpired))
    )
    @cached(cache=TTLCache(maxsize=100, ttl=3600))
    def get_tenant_active_context(self, tenant_name: str, invoice_date: str) -> dict:
        """
        O Oráculo pergunta ao Banco: "Baseado nesta data, quais leis se aplicam?"
        This effectively combats Context Degradation and prevents hallucination
        of future/past tax brackets.
        (Cached for 1 hour to prevent Neo4j Pool Exhaustion under 25k load)
        
        :param tenant_name: Example 'BECO'
        :param invoice_date: String in format 'YYYY-MM-DD'
        :return: A dictionary containing the effective tax rates and framework properties.
        """
        query = """
        MATCH (t:Tenant {name: $tenant_name})-[r:ENFORCES_TAX_POLICY]->(rule:TaxRule)
        WHERE r.valid_from <= $invoice_date AND r.valid_to >= $invoice_date
        RETURN rule.name AS rule_name, rule.authority AS authority, properties(r) AS active_properties
        """
        context_payload = {
            "query_date": invoice_date,
            "tenant": tenant_name,
            "active_rules": []
        }
        
        with self.driver.session() as session:
            result = session.run(query, tenant_name=tenant_name, invoice_date=invoice_date)
            for record in result:
                context_payload["active_rules"].append({
                    "rule_name": record["rule_name"],
                    "authority": record["authority"],
                    "parameters": record["active_properties"]
                })
                
        if not context_payload["active_rules"]:
            logger.warning(f"⚠️ NO ACTIVE TAX CONTEXT found for {tenant_name} on date {invoice_date}. Oracle will operate in the dark!")
            
        return context_payload

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((exceptions.ServiceUnavailable, exceptions.TransientError, exceptions.SessionExpired))
    )
    @cached(cache=TTLCache(maxsize=100, ttl=3600))
    def get_golden_examples(self, tenant_name: str) -> list[dict]:
        """
        Retorna os nós :GoldenExample para o Tenant específico.
        Usado para ancoragem semântica (Few-Shot Prompting / Style LoRA) para redução de alucinações.
        (Cached for 1 hour to prevent DB load)
        """
        query = """
        MATCH (g:GoldenExample {tenant: $tenant_name})
        RETURN g.input_text AS input_text, g.ideal_json AS ideal_json
        """
        golden = []
        with self.driver.session() as session:
            result = session.run(query, tenant_name=tenant_name)
            for record in result:
                golden.append({
                    "input_text": record.get("input_text", ""),
                    "ideal_json": record.get("ideal_json", "")
                })
        
        if golden:
            logger.info(f"✨ Retrieved {len(golden)} GoldenExamples from Graph for Tenant {tenant_name}.")
        return golden

    def inject_entropy_anomaly(self, tenant: str, file_hash: str, error_type: str, raw_errors: str, error_count: int, agent_name: str = "Nicole/BECO"):
        """
        Injects anomaly data into Neo4j.
        Consolidates multiple errors into a single :Anomaly node per document via file hashing
        to prevent database transaction overhead.
        """
        query = """
        // 1. The Origin Document (The failed Invoice)
        // Even on failure, create an :Invoice placeholder to anchor the anomaly context.
        MERGE (i:Invoice:`{tenant_safe}` {file_hash: $file_hash})
        ON CREATE SET i.status = 'QUARANTINED', i.ingested_at = datetime()
        
        // 2. The Anomaly Event (Consolidated Anomaly Node)
        MERGE (a:Anomaly {file_hash: $file_hash})
        SET a.type = $error_type,
            a.count = $error_count,
            a.details = $raw_errors,
            a.timestamp = datetime(),
            a.severity = "High"
            
        // 3. A Assinatura de Inépcia (Quem causou?)
        MERGE (ag:Agent {name: $agent_name})
        MERGE (ag)-[:GENERATED_ANOMALY]->(a)
        
        // 4. Conexão Origem-Destino
        MERGE (i)-[:HAS_ANOMALY]->(a)
        """
        safe_tenant = tenant.replace("`", "")
        params = {
            "tenant_safe": safe_tenant,
            "file_hash": file_hash,
            "error_type": error_type,
            "error_count": error_count,
            "raw_errors": raw_errors,
            "agent_name": agent_name
        }
        try:
            with self.driver.session() as session:
                session.run(query.replace("{tenant_safe}", safe_tenant), **params)
            logger.warning(f"☢️ Anomaly ({error_type}) with {error_count} errors injected into Graph (Tenant: {tenant}).")
        except Exception as e:
            logger.error(f"Failed to inject anomaly into graph for file {file_hash}: {e}")

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD") or os.getenv("NEO4J_PWD")
    
    if not uri or not pwd:
        print("Missing credentials to run Ontology test.")
    else:
        manager = MenirOntologyManager(uri, (user, pwd))
        print("🚀 Executing Base Ontology Bootstrap...")
        manager.bootstrap_system_graph()
        
        print(f"\\n🕒 Querying Active Context for BECO on '2024-05-15':")
        ctx = manager.get_tenant_active_context("BECO", "2024-05-15")
        import json
        print(json.dumps(ctx, indent=2))
        
        print(f"\\n🕒 Querying Active Context for BECO on '1999-01-01' (Should be empty):")
        ctx_old = manager.get_tenant_active_context("BECO", "1999-01-01")
        print(json.dumps(ctx_old, indent=2))
        
        manager.close()
