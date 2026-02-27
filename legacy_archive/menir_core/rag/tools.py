import os
import json
import math
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
from dotenv import load_dotenv

from menir_core.embeddings import embed_text

load_dotenv()

# Initialize driver
_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
_USER = os.getenv("NEO4J_USER", "neo4j")
_PASSWORD = os.getenv("NEO4J_PASSWORD", "menir123")
_DB = os.getenv("NEO4J_DB", "neo4j")

driver = GraphDatabase.driver(_URI, auth=(_USER, _PASSWORD))


def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
        
    return dot_product / (norm_v1 * norm_v2)


def query_narrative_graph(query: str) -> str:
    """
    Query the Menir narrative graph using Cypher.
    
    The graph schema includes:
    - Work, Chapter, ChapterVersion, Scene, Event, Character, Place (nodes)
    - Relationships: Work-[:HAS_CHAPTER]->Chapter, ChapterVersion-[:VERSION_OF]->Chapter,
      ChapterVersion-[:HAS_SCENE]->Scene, Scene-[:NEXT_SCENE]->(next Scene),
      Event-[:OCCURS_IN]->Scene, Event-[:NEXT_EVENT]->(next Event),
      Character-[:APPEARS_IN]->Scene, Scene-[:SET_IN]->Place, etc.
      
    Args:
        query: The Cypher query string.
        
    Returns:
        JSON string of the results.
    """
    # Safety Check: Enforce Read-Only
    forbidden_keywords = ["CREATE", "DELETE", "DETACH", "SET", "MERGE", "REMOVE", "DROP"]
    normalized_query = query.upper()
    for keyword in forbidden_keywords:
        if keyword in normalized_query:
            return json.dumps({"error": f"Write operations are not allowed: Detected '{keyword}'"})

    try:
        with driver.session(database=_DB) as session:
            result = session.run(query)
            # Convert Neo4j records to list of dicts
            data = [record.data() for record in result]
            return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "query": query})


def find_relevant_chunks(query: str, top_k: int = 3) -> str:
    """
    Perform semantic search on narrative text chunks using vector embeddings.
    
    Args:
        query: The user's natural language query.
        top_k: Number of results to return.
        
    Returns:
        JSON string of relevant text chunks with similarity scores.
    """
    try:
        # 1. Embed the query
        query_embedding = embed_text(query)
        
        # 2. Fetch all chunk embeddings from Neo4j
        # Note: For large graphs, use a Vector Index. For Menir's scale, in-memory scan is fine.
        cypher = """
        MATCH (c:Chunk)
        WHERE c.embedding IS NOT NULL
        RETURN c.text AS text, c.embedding AS embedding, c.id AS id
        """
        
        with driver.session(database=_DB) as session:
            result = session.run(cypher)
            chunks = []
            for record in result:
                chunks.append({
                    "text": record["text"],
                    "embedding": record["embedding"],
                    "id": record["id"]
                })
        
        if not chunks:
            return json.dumps({"message": "No chunks found with embeddings."})

        # 3. Compute Similarity
        scored_chunks = []
        for chunk in chunks:
            score = _cosine_similarity(query_embedding, chunk["embedding"])
            scored_chunks.append({
                "score": score,
                "text": chunk["text"],
                "id": chunk["id"]
            })
            
        # 4. Sort and Top-K
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        top_results = scored_chunks[:top_k]
        
        return json.dumps(top_results, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)})

def close_driver():
    driver.close()
