"""
Menir v3.5 Bridge Module
Neo4j Interactions with Pydantic Type Safety & Tenacity Resilience.
"""

import logging
import os

from dotenv import load_dotenv
from neo4j import exceptions
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.v3.core.schemas import BaseNode, Document, Relationship
from src.v3.tenant_middleware import TenantAwareDriver
from src.v3.core.neo4j_pool import get_shared_driver

# Force override to ignore stale shell variables
load_dotenv(override=True)
logger = logging.getLogger("MenirBridge")


class MenirBridge:
    def __init__(self, uri=None, auth=None):
        # Pool credentials and URI are handled by get_shared_driver
        base_driver = get_shared_driver()
        self.driver = TenantAwareDriver(base_driver, db=os.getenv("NEO4J_DB", "neo4j"))

    def close(self):
        # We don't close the shared driver here, just the wrapper if necessary
        # The singleton handles graceful shutdown
        pass

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (exceptions.ServiceUnavailable, exceptions.TransientError, exceptions.SessionExpired)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def check_evidence(self, sha256: str, project: str) -> bool:
        """Recovery Mode Check (Resilient)."""
        if not project:
            raise ValueError("Tenant_ID (project) is required for Context Isolation.")

        safe_tenant = project.replace("`", "")

        query = f"""
        MATCH (d:Document:`{safe_tenant}` {{sha256: $sha, project: $proj}})
        RETURN count(d) > 0 as exists
        """
        with self.driver.session() as session:
            result = session.run(query, sha=sha256, proj=project).single()
            if result and result["exists"]:
                logger.info(f"Recovery Hit: {sha256[:8]}... exists in {project}.")
                return True
            return False

    def check_document_exists(self, sha256: str, tenant_id: str | None = None) -> bool:
        """Alias for check_evidence since Runner calls this."""
        if not tenant_id:
            logger.warning(
                "check_document_exists called without tenant_id. This is a security risk. Denying query."
            )
            return False

        safe_tenant = tenant_id.replace("`", "")
        query = f"MATCH (d:Document:`{safe_tenant}` {{sha256: $sha}}) RETURN count(d) > 0 as exists"
        with self.driver.session() as session:
            result = session.run(query, sha=sha256).single()
            return result["exists"] if result else False

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(
            (exceptions.ServiceUnavailable, exceptions.TransientError, exceptions.SessionExpired)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def merge_node(self, node: BaseNode):
        """
        Type-Safe Node Upsert using Pydantic Models.
        Retries on connection glitches.
        """
        # Extract properties
        # FIX: Do NOT exclude uid. We need it for lookup.
        props = node.model_dump(exclude={"labels"})

        # Flatten 'properties' dict if present (Neo4j cannot store nested maps)
        if "properties" in props and isinstance(props["properties"], dict):
            dynamic_props = props.pop("properties")
            props.update(dynamic_props)

        tenant_id = node.project
        if not tenant_id:
            raise ValueError(
                f"Tenant_ID (project) missing for node {getattr(node, 'name', 'Unknown')}."
            )

        safe_tenant = str(tenant_id).replace("`", "")

        # Dynamic Labels injection
        labels = ":".join([f"`{l}`" for l in node.labels])  # noqa: E741
        labels = f"{labels}:`{safe_tenant}`"

        if isinstance(node, Document):
            query = f"""
            MERGE (n:{labels} {{sha256: $sha256}})
            SET n.project = $project, n += $props, n.ingested_at = datetime()
            """
            params = {"sha256": node.sha256, "project": node.project, "props": props}
        else:
            # Default Entity Logic (Person, Organization)
            # Use name as key + project
            query = f"""
            MERGE (n:{labels} {{name: $name}})
            SET n.project = $project, n += $props
            """
            params = {
                "name": getattr(node, "name", "Unknown"),
                "project": node.project,
                "props": props,
            }

        with self.driver.session() as session:
            session.run(query, **params)
            # No try/except needed here, Tenacity handles the retries.
            # If it fails 5 times, it raises the exception up to the Runner.

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(
            (exceptions.ServiceUnavailable, exceptions.TransientError, exceptions.SessionExpired)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def merge_relationship(self, rel: Relationship):
        """
        Type-Safe Edge Upsert (Resilient).
        """
        tenant_id = rel.properties.get("project")
        if not tenant_id:
            raise ValueError("Tenant_ID (project) missing in Relationship properties.")

        safe_tenant = str(tenant_id).replace("`", "")
        # Sanitizar o tipo de relação para evitar Cypher Injection
        safe_rel_type = rel.relation_type.replace("`", "").replace(" ", "_").upper()

        query = f"""
        MATCH (a:`{safe_tenant}` {{name: $src}})
        MATCH (b:`{safe_tenant}` {{name: $tgt}})
        MERGE (a)-[r:`{safe_rel_type}`]->(b)
        SET r += $props, r.project = $proj
        """

        with self.driver.session() as session:
            session.run(
                query,
                src=rel.source_uid,
                tgt=rel.target_uid,
                proj=rel.properties.get("project", "Menir"),
                props=rel.properties,
            )

    def link_author(self, doc_hash: str, author_name: str, tenant_id: str):
        """
        V3.1: Connects Person to Document.
        Not retried via Tenacity yet (non-critical path), kept as is.
        """
        if not author_name:
            return
        if not tenant_id:
            logger.error("link_author called without tenant_id. Skipping to prevent data leak.")
            return

        safe_tenant = str(tenant_id).replace("`", "")
        safe_name = author_name.replace("'", "").strip()
        first_name = safe_name.split()[0] if " " in safe_name else safe_name

        query_exact = f"""
        MATCH (p:Person:`{safe_tenant}`) WHERE toLower(p.name) = toLower($name)
        MATCH (d:Document:`{safe_tenant}` {{sha256: $sha}})
        MERGE (p)-[:WROTE {{match_type: 'EXACT'}}]->(d)
        RETURN p.name as linked_name
        """

        query_fuzzy = f"""
        MATCH (p:Person:`{safe_tenant}`)   # noqa: W291
        WHERE toLower(p.name) STARTS WITH toLower($first_name)
          AND abs(size(p.name) - size($name)) <= 2
          AND toLower(p.name) <> toLower($name)
        WITH collect(p) as candidates
        WHERE size(candidates) = 1
        UNWIND candidates as p
        MATCH (d:Document:`{safe_tenant}` {{sha256: $sha}})
        MERGE (p)-[:WROTE {{match_type: 'FUZZY'}}]->(d)
        RETURN p.name as linked_name
        """

        try:
            with self.driver.session() as session:
                # 1. Try Exact
                result = session.run(query_exact, name=safe_name, sha=doc_hash).single()
                if result:
                    logger.info(
                        f"Metadata Link: Linked '{safe_name}' to '{result['linked_name']}' (EXACT)."
                    )
                    return

                # 2. Try Fuzzy
                result = session.run(
                    query_fuzzy, name=safe_name, first_name=first_name, sha=doc_hash
                ).single()
                if result:
                    logger.info(
                        f"Metadata Link: Linked '{safe_name}' to '{result['linked_name']}' (FUZZY)."
                    )
                else:
                    logger.info(
                        f"Metadata Link: Author '{safe_name}' not found or ambiguous (Skipped)."
                    )

        except Exception as e:
            logger.exception(f"Metadata Link Error: {e}")

    def init_vector_index(self):
        """
        Creates a Vector Index for Native RAG.
        Dimensions: 384 (all-MiniLM-L6-v2)
        Similarity: Cosine
        """
        query = """
        CREATE VECTOR INDEX menir_vectors IF NOT EXISTS
        FOR (c:Chunk) ON (c.embedding)
        OPTIONS {indexConfig: {
            `vector.dimensions`: 384,
            `vector.similarity_function`: 'cosine'
        }}
        """
        try:
            with self.driver.session() as session:
                session.run(query)
                logger.info("✅ Native Vector Index 'menir_vectors' Ready.")
        except exceptions.ClientError as e:
            if "already exists" in str(e).lower() or "equivalent" in str(e).lower():
                logger.info("ℹ️ Vector Index 'menir_vectors' already exists.")  # noqa: RUF001
            else:
                logger.warning(f"Vector Index Init Warning: {e}")
        except Exception as e:
            logger.warning(f"Vector Index Init Warning: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def merge_chunk(self, chunk_id: str, text: str, embedding: list, doc_sha: str, tenant_id: str):
        """
        Ingests a Text Chunk with Vector Embedding.
        Links it to the parent Document.
        """
        if not tenant_id:
            raise ValueError("Tenant_ID is required for merge_chunk.")
        safe_tenant = str(tenant_id).replace("`", "")

        query = f"""
        MATCH (d:Document:`{safe_tenant}` {{sha256: $doc_sha}})
        MERGE (c:Chunk:`{safe_tenant}` {{uid: $uid}})
        SET c.name = $uid,
            c.text = $text,   # noqa: W291
            c.embedding = $embedding,
            c.generated_at = datetime()
        MERGE (c)-[:BELONGS_TO]->(d)
        """
        with self.driver.session() as session:
            session.run(query, uid=chunk_id, text=text, embedding=embedding, doc_sha=doc_sha)

    def vector_search(
        self, embedding: list, tenant_id: str, limit: int = 5, min_score: float = 0.7
    ):
        """
        Performs KNN Search on the Vector Index, filtered by Tenant_ID.
        """
        if not tenant_id:
            raise ValueError("Tenant_ID is required to prevent data leakage in Vector Search.")
        safe_tenant = str(tenant_id).replace("`", "")

        query = f"""
        CALL db.index.vector.queryNodes('menir_vectors', $limit, $embedding)
        YIELD node, score
        WHERE score >= $min_score AND '{safe_tenant}' IN labels(node)
        RETURN node.text as text, score, node.uid as uid
        """
        with self.driver.session() as session:
            result = session.run(query, limit=limit, embedding=embedding, min_score=min_score)
            return [{"text": r["text"], "score": r["score"]} for r in result]
