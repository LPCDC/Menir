"""
Menir Core V5.1 - Meta Cognition Layer
Stores, manages, and queries the system's own architectural topology
and the strict temporal Tax Ontology for Swiss ERP Integrations (Crésus).
"""

import logging
from typing import TYPE_CHECKING, TypeVar

from cachetools import TTLCache, cached
from neo4j import GraphDatabase, exceptions
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

if TYPE_CHECKING:
    from pydantic import BaseModel

T = TypeVar("T", bound="BaseModel")

logger = logging.getLogger("MetaCognition")


class MenirOntologyManager:
    """
    Manages the architectural blueprint and temporal fiscal rules
    directly within the Neo4j instance to ensure the Oracles remain
    grounded physically and temporally.
    """

    def __init__(self, uri: str, auth: tuple, db_name: str = "neo4j"):
        self.driver = GraphDatabase.driver(
            uri, auth=auth, max_connection_pool_size=50, connection_acquisition_timeout=60.0
        )
        self.db_name = db_name
        self.db_name = db_name

    def close(self):
        self.driver.close()

    def from_neo4j(self, node_data: dict, model: type[T]) -> T:
        """
        OGM Factory Layer. (Phase 40 Strict Hardening)
        Strict=True ensures zero-tolerance for type coercion and schema hallucination.
        """
        try:
            instance = model.model_validate(node_data, strict=True)
            return instance
        except Exception as e:
            logger.error(f"❌ Failed Strict OGM parsing for {model.__name__}: {e}")
            raise

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (exceptions.ServiceUnavailable, exceptions.TransientError, exceptions.SessionExpired)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def bootstrap_system_graph(self):
        """
        Injects the immutable Base Ontology and specific BECO ERP logic.
        Uses pure Cypher to guarantee schema rigidity and temporal constraints.
        """
        logger.info("Initializing Meta-Cognition: Bootstrapping System Ontology...")

        query = """
        // 1. A Arquitetura Fundacional (Kernel Ontology - Phase 32)
        MERGE (dev:Developer {name: "Luiz Oak", role: "Arquiteto Chefe"})
        MERGE (core:CoreSystem {name: "Menir", version: "5.2", engine: "Metacognitive Oracle"})
        MERGE (dev)-[:ARCHITECTED]->(core)

        // Mapeando Pipelines e Dependências Vitais
        MERGE (p_runner:Pipeline {name: "WatchdogDispatcher", type: "Async_Ingestion"})
        MERGE (p_mcp:Pipeline {name: "WebMCP_Gateway", type: "JSON_RPC_Interceptor"})
          # noqa: W293
        MERGE (d_neo:Dependency {name: "AuraDB", criticality: "FATAL"})
        ON CREATE SET d_neo.is_active = true
        MERGE (d_llm:Dependency {name: "VertexAI", criticality: "FATAL"})
        ON CREATE SET d_llm.is_active = true
          # noqa: W293
        // Regras Operacionais (Rules)
        MERGE (r_iso:Rule {name: "GalvanicIsolation", type: "Tenant_Boundary"})
        MERGE (r_anti:Rule {name: "ZeroBloat", type: "Architectural_Constraint"})

        // Conectando o Sistema Nervoso
        MERGE (core)-[:EXECUTES]->(p_runner)
        MERGE (core)-[:EXECUTES]->(p_mcp)
        MERGE (p_runner)-[:DEPENDS_ON]->(d_neo)
        MERGE (p_runner)-[:DEPENDS_ON]->(d_llm)
        MERGE (p_mcp)-[:DEPENDS_ON]->(d_neo)
          # noqa: W293
        MERGE (core)-[:MUST_OBEY]->(r_iso)
        MERGE (core)-[:MUST_OBEY]->(r_anti)

        // 2. O Tenant BECO e as Leis Suiças (Temporalidade Ativa - Crésus ERP)
        MERGE (tenant:Tenant {name: "BECO", target_erp: "Crésus"})
        MERGE (core)-[:SERVES_TENANT]->(tenant)
          # noqa: W293
        // Criando as regras macro da AFC Suiça (Administração Federal das Contribuições)
        MERGE (rule_tdfn:TaxRule {name: "TDFN_Framework", authority: "ESTV/AFC"})
        MERGE (rule_effective:TaxRule {name: "TVA_Effective", authority: "ESTV/AFC"})
          # noqa: W293
        // Arestas TEMPORAIS (Conectando a BECO às regras com validades de datas)
        MERGE (tenant)-[rt:ENFORCES_TAX_POLICY]->(rule_tdfn)
        SET rt.valid_from = "2024-01-01",   # noqa: W291
            rt.valid_to = "2099-12-31",   # noqa: W291
            rt.default_eur_chf_rate = 0.912
              # noqa: W293
        MERGE (tenant)-[rt_tva:ENFORCES_TAX_POLICY]->(rule_effective)
        SET rt_tva.valid_from = "2024-01-01",   # noqa: W291
            rt_tva.valid_to = "2099-12-31",
            rt_tva.standard_rate = 8.1,
            rt_tva.reduced_rate = 2.6,
            rt_tva.special_rate = 3.8

        RETURN core.name, tenant.name
        """
        with self.driver.session(database=self.db_name) as session:
            session.run(query)
            logger.info(
                "✅ Core System Ontology (Kernel) & Swiss Tax Rules successfully injected into the Graph."
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type(
            (exceptions.ServiceUnavailable, exceptions.TransientError, exceptions.SessionExpired)
        ),
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
        query_rules = """
        MATCH (t:Tenant {name: $tenant_name})-[r:ENFORCES_TAX_POLICY]->(rule:TaxRule)
        WHERE r.valid_from <= $invoice_date AND r.valid_to >= $invoice_date
        RETURN rule.name AS rule_name, rule.authority AS authority, properties(r) AS active_properties
        """
        query_tva = """
        MATCH (t:Tenant {name: $tenant_name})-[:HAS_TVA_RATE]->(tr:TVARate)
        RETURN tr.rate AS rate, tr.label AS label
        """
        from typing import Any
        context_payload: dict[str, Any] = {
            "query_date": invoice_date,
            "tenant": tenant_name,
            "active_rules": [],
            "tva_rates": [],
        }

        with self.driver.session(database=self.db_name) as session:
            # Fetch generic temporal rules
            result = session.run(query_rules, tenant_name=tenant_name, invoice_date=invoice_date)
            for record in result:
                context_payload["active_rules"].append(
                    {
                        "rule_name": record["rule_name"],
                        "authority": record["authority"],
                        "parameters": record["active_properties"],
                    }
                )

            # Fetch explicit TVA rates
            result_tva = session.run(query_tva, tenant_name=tenant_name)
            for record in result_tva:
                context_payload["tva_rates"].append(float(record["rate"]))

        if not context_payload["active_rules"] and not context_payload["tva_rates"]:
            logger.warning(
                f"⚠️ NO ACTIVE TAX CONTEXT found for {tenant_name} on date {invoice_date}. Oracle will operate in the dark!"
            )

        return context_payload

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type(
            (exceptions.ServiceUnavailable, exceptions.TransientError, exceptions.SessionExpired)
        ),
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
        with self.driver.session(database=self.db_name) as session:
            result = session.run(query, tenant_name=tenant_name)
            for record in result:
                golden.append(
                    {
                        "input_text": record.get("input_text", ""),
                        "ideal_json": record.get("ideal_json", ""),
                    }
                )

        if golden:
            logger.info(
                f"✨ Retrieved {len(golden)} GoldenExamples from Graph for Tenant {tenant_name}."
            )
        return golden

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        retry=retry_if_exception_type(
            (exceptions.ServiceUnavailable, exceptions.TransientError, exceptions.SessionExpired)
        ),
    )
    def check_system_health(self) -> bool:
        """
        Preemptive Meta-Diagnostic (Phase 32).
        The architecture queries its own topology to verify if all FATAL dependencies
        are marked as active before execution continues.
        Acts as a 'Circuit Breaker' to prevent executing costly LLM APIs when infra is failing.
        """
        query = """
        MATCH (core:CoreSystem)-[:EXECUTES]->(p:Pipeline)-[:DEPENDS_ON]->(d:Dependency)
        WHERE d.is_active = false AND d.criticality = 'FATAL'
        RETURN p.name AS pipeline, d.name AS dependency
        """
        with self.driver.session(database=self.db_name) as session:
            result = session.run(query)
            failures = [
                {"pipeline": record["pipeline"], "dependency": record["dependency"]}
                for record in result
            ]

            if failures:
                logger.error(
                    f"❌ KERNEL PANIC: System Health Check failed! Dead dependencies found: {failures}"
                )
                logger.error("Circuit Breaker Tripped. Standby enforced.")
                return False

            logger.debug("✅ Kernel Health Check: All FATAL dependencies are active.")
            return True

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(
            (exceptions.ServiceUnavailable, exceptions.TransientError, exceptions.SessionExpired)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def inject_entropy_anomaly(
        self,
        tenant: str,
        file_hash: str,
        error_type: str,
        raw_errors: str,
        error_count: int,
        agent_name: str = "Nicole/BECO",
    ):
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
          # noqa: W293
        // 2. The Anomaly Event (Consolidated Anomaly Node)
        MERGE (a:Anomaly {file_hash: $file_hash})
        SET a.type = $error_type,
            a.count = $error_count,
            a.details = $raw_errors,
            a.timestamp = datetime(),
            a.severity = "High"
              # noqa: W293
        // 3. A Assinatura de Inépcia (Quem causou?)
        MERGE (ag:Agent {name: $agent_name})
        MERGE (ag)-[:GENERATED_ANOMALY]->(a)
          # noqa: W293
        // 4. Conexão Origem-Destino (Rule 12: Errors mapped via RECONCILED)
        MERGE (i)-[r:RECONCILED]->(a)
        SET r.status = 'FAILED_VALIDATION'
        """
        safe_tenant = tenant.replace("`", "")
        from typing import Any
        params: dict[str, Any] = {
            "tenant_safe": safe_tenant,
            "file_hash": file_hash,
            "error_type": error_type,
            "error_count": error_count,
            "raw_errors": raw_errors,
            "agent_name": agent_name,
        }
        try:
            with self.driver.session() as session:
                session.run(query.replace("{tenant_safe}", safe_tenant), **params)
            logger.warning(
                f"☢️ Anomaly ({error_type}) with {error_count} errors injected into Graph (Tenant: {tenant})."
            )
        except Exception as e:
            logger.error(f"Failed to inject anomaly into graph for file {file_hash}: {e}")


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv(override=True)

    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD") or os.getenv("NEO4J_PWD")
    db = os.getenv("NEO4J_DB", "neo4j")

    if not uri or not pwd:
        print("Missing credentials to run Ontology test.")
    else:
        manager = MenirOntologyManager(uri, (user, pwd), db_name=db)
        print("🚀 Executing Base Ontology Bootstrap...")
        manager.bootstrap_system_graph()

        print("\\n🕒 Querying Active Context for BECO on '2024-05-15':")
        ctx = manager.get_tenant_active_context("BECO", "2024-05-15")
        import json

        print(json.dumps(ctx, indent=2))

        print("\\n🕒 Querying Active Context for BECO on '1999-01-01' (Should be empty):")
        ctx_old = manager.get_tenant_active_context("BECO", "1999-01-01")
        print(json.dumps(ctx_old, indent=2))

        print("\\n🩺 Running Kernel Health Check...")
        manager.check_system_health()

        manager.close()
