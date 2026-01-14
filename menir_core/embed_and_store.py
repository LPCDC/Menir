"""
Pipeline mínimo de embeddings para o Menir v10.4.1:
- Conecta no Neo4j (Aura ou local) usando NEO4J_URI / USER / PASSWORD.
- Armazena embeddings como LIST<FLOAT> (sem usar neo4j.vector.Vector).
- Permite fetch de chunks para debug.
"""

import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def store_chunk(
    chunk_id: str,
    text: str,
    embedding: List[float],
    metadata: Dict[str, Any] | None = None,
) -> None:
    """
    Cria/atualiza um nó :DocumentChunk com:
      - id (string)
      - text (string)
      - embedding (LIST<FLOAT>)
      - metadata_json (string - JSON serialized)
    """
    if metadata is None:
        metadata = {}

    metadata_json = json.dumps(metadata)

    with driver.session() as session:
        session.run(
            """
            MERGE (d:DocumentChunk {id: $id})
            SET d.text           = $text,
                d.embedding      = $embedding,
                d.metadata_json  = $metadata_json
            """,
            id=chunk_id,
            text=text,
            embedding=embedding,
            metadata_json=metadata_json,
        )


def fetch_chunks(prefix: str = "test:", limit: int = 10) -> List[Dict[str, Any]]:
    """
    Busca nós :DocumentChunk para inspeção rápida.
    """
    with driver.session() as session:
        result = session.run(
            """
            MATCH (d:DocumentChunk)
            WHERE d.id STARTS WITH $prefix
            RETURN d.id AS id, d.text AS text, d.embedding AS embedding
            LIMIT $limit
            """,
            prefix=prefix,
            limit=limit,
        )
        return [dict(r) for r in result]


def close_driver() -> None:
    driver.close()


if __name__ == "__main__":
    # Pequeno smoke test manual
    dummy_id = "test:dummy"
    dummy_text = "chunk de teste do Menir"
    dummy_emb = [float(i) for i in range(8)]

    print(f"[embed_and_store] Gravando {dummy_id} em {NEO4J_URI} como LIST<FLOAT>...")
    store_chunk(dummy_id, dummy_text, dummy_emb, {"source": "manual_main"})

    print("[embed_and_store] Lendo de volta:")
    rows = fetch_chunks(prefix="test:", limit=5)
    for row in rows:
        print(row)

    close_driver()
