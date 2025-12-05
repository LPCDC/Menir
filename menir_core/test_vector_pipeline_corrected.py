"""Vector pipeline smoke test against Neo4j with vector index.

Requirements:
- Neo4j with vector indexes enabled
- Env vars: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
- Vector index named 'doc_embedding_idx' on :DocumentChunk(embedding)

This script is ad-hoc and not part of automated pytest runs.
"""
import os
import random
import string
import sys

import numpy as np
from neo4j import GraphDatabase
from neo4j.vector import Vector

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def random_embedding(dim: int = 8) -> np.ndarray:
    """Generate a random float32 embedding."""
    return np.random.random(dim).astype(np.float32)


def test_store_and_query():
    chunk_id = "test_chunk_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    text = "This is a test chunk for embedding storage and retrieval."
    emb = random_embedding(dim=8)
    vec = Vector.from_numpy(emb)

    with driver.session() as session:
        session.run(
            """
            MERGE (c:DocumentChunk {id: $id})
            SET c.text = $text,
                c.embedding = $vector,
                c.source = $source
            """,
            {"id": chunk_id, "text": text, "vector": vec, "source": "test"},
        )

    with driver.session() as session:
        result = session.run(
            """
            MATCH (c:DocumentChunk {id: $id})
            WITH c.embedding AS v
            CALL db.index.vector.queryNodes('doc_embedding_idx', 5, v) YIELD node, score
            RETURN node.id AS id, score
            ORDER BY score DESC
            LIMIT 5
            """,
            {"id": chunk_id},
        )
        rows = [r.data() for r in result]

    if not rows:
        print("❌ ERRO: nenhuma linha retornada na query de similaridade")
        sys.exit(1)

    top = rows[0]
    if top["id"] != chunk_id:
        print("❌ ERRO: o top result não é o chunk inserido — resultados:", rows)
        sys.exit(1)

    print("✅ OK — pipeline vetor funcionando. Resultado:", rows)
    driver.close()


if __name__ == "__main__":
    test_store_and_query()
