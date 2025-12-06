# menir_core/graph_ingest.py

from __future__ import annotations
import os
import sys
import textwrap
from dataclasses import dataclass
from typing import Iterable, List
from pathlib import Path

from neo4j import GraphDatabase

# Handle both module import and direct execution
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from menir_core.embeddings import embed_text
else:
    from .embeddings import embed_text


NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "menir123")
MENIR_PROJECT_ID = os.getenv("MENIR_PROJECT_ID", "default_project")


@dataclass
class Chunk:
    index: int
    text: str
    embedding: List[float]


def _chunk_text(text: str, max_chars: int = 800) -> List[str]:
    """Chunk muito simples por tamanho; depois podemos sofisticar por sentença etc."""
    text = text.strip()
    if not text:
        return []
    return [
        text[i : i + max_chars]
        for i in range(0, len(text), max_chars)
    ]


def _prepare_chunks(text: str) -> List[Chunk]:
    raw_chunks = _chunk_text(text)
    chunks: List[Chunk] = []
    for idx, t in enumerate(raw_chunks):
        emb = embed_text(t)
        chunks.append(Chunk(index=idx, text=t, embedding=emb))
    return chunks


def ingest_document(doc_id: str, title: str, full_text: str) -> int:
    """
    Ingesta um documento no grafo Menir:

    - Cria/MERGE (p:Project {id: MENIR_PROJECT_ID})
    - Cria/MERGE (d:Document {id: doc_id})
    - Cria/MERGE chunks (:Chunk) com vetores
    - Liga nós com [:PART_OF] e [:HAS_CHUNK]
    """
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    chunks = _prepare_chunks(full_text)

    def _tx_ingest(tx, doc_id: str, title: str, chunks: Iterable[Chunk]) -> int:
        # Document + Project
        tx.run(
            """
            MERGE (p:Project {id: $project_id})
              ON CREATE SET p.created_at = datetime()
            MERGE (d:Document {id: $doc_id})
              ON CREATE SET d.created_at = datetime()
            SET d.title = $title,
                d.updated_at = datetime()
            WITH d, p
            MERGE (d)-[:PART_OF]->(p)
            """,
            project_id=MENIR_PROJECT_ID,
            doc_id=doc_id,
            title=title,
        )

        # Chunks com embedding
        for c in chunks:
            tx.run(
                """
                MATCH (d:Document {id: $doc_id})
                MERGE (ch:Chunk {id: $chunk_id})
                  ON CREATE SET ch.created_at = datetime()
                SET ch.index = $index,
                    ch.text = $text,
                    ch.embedding = $embedding,
                    ch.updated_at = datetime()
                WITH d, ch
                MERGE (ch)-[:PART_OF]->(d)
                WITH d, ch
                MERGE (d)-[:HAS_CHUNK]->(ch)
                """,
                doc_id=doc_id,
                chunk_id=f"{doc_id}::chunk::{c.index}",
                index=c.index,
                text=c.text,
                embedding=c.embedding,
            )

        # Retorna contagem de chunks
        result = tx.run(
            """
            MATCH (:Document {id: $doc_id})-[:HAS_CHUNK]->(ch:Chunk)
            RETURN count(ch) AS n
            """,
            doc_id=doc_id,
        )
        record = result.single()
        return record["n"] if record else 0

    with driver.session() as session:
        count = session.execute_write(_tx_ingest, doc_id, title, chunks)

    driver.close()
    return count


def ingest_markdown_file(path: str, doc_id: str | None = None, title: str | None = None) -> int:
    """
    Helper para ingestão de um arquivo .md (ou .txt) local.
    """
    if doc_id is None:
        doc_id = os.path.basename(path)
    if title is None:
        title = doc_id

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    return ingest_document(doc_id=doc_id, title=title, full_text=content)


if __name__ == "__main__":
    sample_text = textwrap.dedent(
        """
        Este é um teste de ingestão do Menir.
        Podemos colocar aqui um trecho mais longo, como um resumo do caso Itaú,
        um capítulo do livro da Débora ou um dump de conversa do Menir.
        O Menir é um sistema de memória pessoal que combina grafos de conhecimento
        com embeddings vetoriais para navegação semântica. Criado por Luiz para
        ajudar Débora a estruturar seu livro, o Menir evoluiu para uma plataforma
        de autorreflexão e organização de narrativas complexas.
        """
    )
    print(f"📝 Texto: {len(sample_text)} caracteres")
    n = ingest_document("demo_ingest_001", "Demo Ingestão", sample_text)
    print(f"✅ Ingestão concluída com {n} chunks.")
