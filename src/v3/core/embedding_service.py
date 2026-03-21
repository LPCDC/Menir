"""
embedding_service.py — Serviço de embedding async para o Menir OS.

Responsabilidades:
  1. Gerar embeddings via google-genai>=1.0.0 de forma não-bloqueante.
  2. Persistir embedding no nó Neo4j correspondente.
  3. Nunca bloquear o event loop principal — toda I/O via asyncio.to_thread.
  4. Retry automático para rate-limits da API Gemini (Tenacity).

Uso:
  # Após criar/atualizar um Lead:
  asyncio.create_task(
      EmbeddingService.embed_and_persist(node_id, text, label="Lead")
  )
  # Fire-and-forget — não awaitar no hot path.
"""

import asyncio
import logging
from typing import Literal

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

# GEMINI_EMBEDDING_MODEL might not be defined in config yet, let's hardcode the fallback if needed, or import from config.
# Wait, I don't see config defining GEMINI_EMBEDDING_MODEL. I will use 'models/gemini-embedding-001'.
GEMINI_EMBEDDING_MODEL = "models/gemini-embedding-001"

from src.v3.core.neo4j_pool import get_shared_driver
from src.v3.core.concurrency import run_in_custom_executor, io_pool

logger = logging.getLogger("menir.embedding")

# Tipos de nós que suportam embedding
EmbeddableLabel = Literal["Lead", "Event", "Product", "Concept"]


class EmbeddingService:
    """
    Serviço singleton de geração e persistência de embeddings.
    Todos os métodos são async e não-bloqueantes.
    """

    @classmethod
    def _get_intel(cls):
        """Lazy init do MenirIntel para compartilhar o Rate Limiter (Aiolimiter)"""
        if not hasattr(cls, "_intel_singleton"):
            from src.v3.menir_intel import MenirIntel
            cls._intel_singleton = MenirIntel()
        return cls._intel_singleton

    @staticmethod
    def _persist_embedding_sync(
        node_label: str,
        node_id: str,
        embedding: list[float],
        tenant: str,
    ) -> None:
        """
        Persiste o embedding no nó Neo4j.
        Síncrono — encapsulado para uso via asyncio.to_thread.
        """
        safe_tenant = tenant.replace("`", "").replace(";", "")
        query = f"""
        MATCH (n:{node_label}:`{safe_tenant}` {{uid: $node_id}})
        SET n.embedding = $embedding,
            n.embedded_at = datetime()
        """
        driver = get_shared_driver()
        with driver.session() as session:
            session.run(query, node_id=node_id, embedding=embedding)

    @classmethod
    async def embed_and_persist(
        cls,
        node_id: str,
        text: str,
        label: EmbeddableLabel,
        tenant: str,
    ) -> None:
        """
        Pipeline completo: gerar embedding → persistir no Neo4j.
        Fire-and-forget via asyncio.create_task().
        NUNCA awaitar no hot path do Watchdog.
        """
        try:
            logger.debug(f"Gerando embedding para {label}:{node_id}")

            # Etapa 1: gerar embedding (Rate Limited inside MenirIntel)
            embedding = await cls._get_intel().generate_embedding(text)
            
            if not embedding:
                raise ValueError("Falha na geração de embedding: Retorno vazio do Gemini.")

            # Etapa 2: persistir no grafo (I/O de rede — custom executor)
            await run_in_custom_executor(
                io_pool,
                cls._persist_embedding_sync,
                label, node_id, embedding, tenant
            )

            logger.info(f"✅ Embedding persistido: {label}:{node_id}")

        except Exception:
            logger.exception(
                f"Falha ao gerar/persistir embedding para {label}:{node_id}. "
                f"Nó continua funcional sem embedding — busca vetorial indisponível "
                f"para este item até próxima tentativa."
            )

    @classmethod
    async def semantic_search(
        cls,
        query_text: str,
        label: EmbeddableLabel,
        tenant: str,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Busca semântica por similaridade de cosseno.
        Retorna os top_k nós mais similares ao query_text.
        """
        try:
            query_embedding = await cls._get_intel().generate_embedding(query_text)
            
            if not query_embedding:
                return []

            index_name = f"{label.lower()}_intent_index"

            def _search():
                driver = get_shared_driver()
                with driver.session() as session:
                    result = session.run(
                        f"""
                        CALL db.index.vector.queryNodes(
                            $index_name, $top_k, $embedding
                        )
                        YIELD node AS n, score
                        WHERE n:`{tenant.replace('`','')}`
                        RETURN n.uid AS id,
                               n.name AS name,
                               n.status AS status,
                               score
                        ORDER BY score DESC
                        """,
                        index_name=index_name,
                        top_k=top_k,
                        embedding=query_embedding,
                    )
                    return [record.data() for record in result]

            return await run_in_custom_executor(io_pool, _search)

        except Exception:
            logger.exception(f"Falha na busca semântica para: {query_text[:60]}")
            return []
