
"""
Vector Search Test (Horizon 4)
Performs a semantic search against the `Chunk` vector index.
"""
import logging
import argparse
from src.v3.ingestion_engine import GeminiEmbedder
from src.v3.menir_bridge import MenirBridge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QueryVector")

def search(text: str, top_k: int = 3):
    embedder = GeminiEmbedder()
    bridge = MenirBridge()
    
    logger.info(f"🔎 Embedding Query: '{text}'...")
    query_vector = embedder.embed(text)
    
    # Neo4j Vector Search Query
    cypher = """
    CALL db.index.vector.queryNodes('chunk_embeddings', $k, $vector)
    YIELD node, score
    RETURN node.text as text, node.source as source, score
    """
    
    with bridge.driver.session() as session:
        logger.info(f"📡 Querying Neo4j for Top {top_k} matches...")
        results = session.run(cypher, k=top_k, vector=query_vector).data()
        
        if not results:
            print("❌ No matches found.")
        else:
            print(f"\n🎯 Found {len(results)} matches:\n")
            for i, r in enumerate(results, 1):
                print(f"[{i}] Score: {r['score']:.4f}")
                print(f"    Source: {r['source']}")
                print(f"    Text: {r['text'][:200]}...")
                print("-" * 20)

    bridge.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Menir Vector Search Utility")
    parser.add_argument("query", help="Text to search for")
    parser.add_argument("--k", type=int, default=3, help="Top K results")
    
    args = parser.parse_args()
    search(args.query, args.k)
