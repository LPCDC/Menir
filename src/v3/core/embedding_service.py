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

logger = logging.getLogger("menir.embedding")

# Tipos de nós que suportam embedding
EmbeddableLabel = Literal["Lead", "Event", "Product", "Concept"]


class EmbeddingService:
    """
    Serviço singleton de geração e persistência de embeddings.
    Todos os métodos são async e não-bloqueantes.
    """

    _client = None

    @classmethod
    def _get_client(cls):
        """Lazy init do client Gemini — evita import circular."""
        if cls._client is None:
            from google import genai
            import os
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY não definido no ambiente.")
            cls._client = genai.Client(api_key=api_key)
        return cls._client

    @staticmethod
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def _generate_embedding_sync(text: str) -> list[float]:
        """
        Chama a API de embedding de forma síncrona.
        Encapsulada para uso via asyncio.to_thread.
        O @retry do Tenacity lida com rate-limits (429) e erros transientes.
        """
        from google.genai import types
        client = EmbeddingService._get_client()
        result = client.models.embed_content(
            model=GEMINI_EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(output_dimensionality=768)
        )
        return result.embeddings[0].values

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
        MATCH (n:{node_label}:`{safe_tenant}` {{id: $node_id}})
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

            # Etapa 1: gerar embedding (I/O de rede — to_thread)
            embedding = await asyncio.to_thread(
                cls._generate_embedding_sync, text
            )

            # Etapa 2: persistir no grafo (I/O de rede — to_thread)
            await asyncio.to_thread(
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
            query_embedding = await asyncio.to_thread(
                cls._generate_embedding_sync, query_text
            )

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
                        RETURN n.id AS id,
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

            return await asyncio.to_thread(_search)

        except Exception:
            logger.exception(f"Falha na busca semântica para: {query_text[:60]}")
            return []
