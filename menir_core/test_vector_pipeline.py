"""
Teste mínimo de pipeline de embeddings para o Menir:
- Usa o mesmo driver do embed_and_store (NEO4J_URI / USER / PASSWORD).
- Cria alguns :DocumentChunk de teste com embedding = LIST<FLOAT>.
- Calcula similaridade em Python (cosine) para verificar round-trip.
- Não usa neo4j.vector.Vector (nem índice vetorial ainda).
"""

import os
from typing import Any, Dict, List

from dotenv import load_dotenv
import numpy as np
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def _cosine_sim(a: List[float], b: List[float]) -> float:
    va = np.array(a, dtype=float)
    vb = np.array(b, dtype=float)
    denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
    if denom == 0.0:
        return 0.0
    return float(va @ vb / denom)


def test_store_and_query() -> None:
    """
    - Apaga chunks de teste antigos (id começando com 'test:vec:').
    - Cria 3 chunks com embeddings simples.
    - Busca tudo de volta e calcula similaridade no Python.
    """
    with driver.session() as session:
        # Limpa lixo anterior de teste
        session.run(
            """
            MATCH (d:DocumentChunk)
            WHERE d.id STARTS WITH 'test:vec:'
            DETACH DELETE d
            """
        )

        base_emb = [0.1, 0.2, 0.3, 0.4]
        samples: List[Dict[str, Any]] = [
            {"id": "test:vec:a", "text": "chunk A (muito parecido)", "emb": [0.11, 0.21, 0.31, 0.39]},
            {"id": "test:vec:b", "text": "chunk B (oposto)",          "emb": [-0.1, -0.2, -0.3, -0.4]},
            {"id": "test:vec:c", "text": "chunk C (neutro)",          "emb": [0.0, 0.1, 0.0, 0.1]},
        ]

        # Cria nós de teste
        for s in samples:
            session.run(
                """
                CREATE (d:DocumentChunk {
                    id:   $id,
                    text: $text,
                    embedding: $emb
                })
                """,
                id=s["id"],
                text=s["text"],
                emb=s["emb"],
            )

        # Lê de volta
        result = session.run(
            """
            MATCH (d:DocumentChunk)
            WHERE d.id STARTS WITH 'test:vec:'
            RETURN d.id AS id, d.text AS text, d.embedding AS embedding
            """
        )
        rows = [dict(r) for r in result]

    print(f"[test_vector_pipeline] Conectado em: {NEO4J_URI}")
    print(f"[test_vector_pipeline] {len(rows)} chunks de teste encontrados.")

    scored = [
        {
            "id": row["id"],
            "sim": _cosine_sim(base_emb, row["embedding"]),
            "text": row["text"],
        }
        for row in rows
    ]
    scored.sort(key=lambda x: x["sim"], reverse=True)

    print("[test_vector_pipeline] Similaridade em relação ao embedding base:")
    for s in scored:
        print(f"  {s['id']}: sim={s['sim']:.4f} | {s['text']}")


if __name__ == "__main__":
    try:
        test_store_and_query()
    finally:
        driver.close()
