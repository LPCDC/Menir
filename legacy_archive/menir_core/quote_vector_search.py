# menir_core/quote_vector_search.py

from __future__ import annotations
import math
import os
import sys
from typing import List, Tuple
from pathlib import Path

from neo4j import GraphDatabase

# Handle both module import and direct execution
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from menir_core.embeddings import embed_text
else:
    from .embeddings import embed_text

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "menir123")


def _cosine(a: List[float], b: List[float]) -> float:
    num = sum(x * y for x, y in zip(a, b))
    da = math.sqrt(sum(x * x for x in a))
    db = math.sqrt(sum(x * x for x in b))
    if da == 0 or db == 0:
        return 0.0
    return num / (da * db)


def _fetch_quotes(tx):
    result = tx.run(
        """
        MATCH (q:Quote)-[:MENTIONS_TOPIC]->(t:Topic)
        RETURN q.id AS id,
               q.text AS text,
               collect(DISTINCT t.name) AS topics
        """
    )
    return [r.data() for r in result]


def search_quotes(query: str, top_k: int = 5) -> List[Tuple[float, dict]]:
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    with driver.session() as session:
        quotes = session.execute_read(_fetch_quotes)

    q_vec = embed_text(query)
    scored: List[Tuple[float, dict]] = []

    for q in quotes:
        v = embed_text(q["text"])
        sim = _cosine(q_vec, v)
        scored.append((sim, q))

    scored.sort(key=lambda x: x[0], reverse=True)
    driver.close()
    return scored[:top_k]


def cli_main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    results = search_quotes(args.query, top_k=args.top_k)
    print(f"Top {args.top_k} resultados para: {args.query!r}\n")
    for sim, q in results:
        topics = ", ".join(q["topics"])
        print(f"{sim:.4f} | {q['id']} | [{topics}]")
        print(f"  {q['text']}\n")


if __name__ == "__main__":
    cli_main()
