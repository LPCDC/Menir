import sys
import os
import time

# Add /app to pythonpath
sys.path.append("/app")

from neo4j import GraphDatabase
from menir_core.embeddings import embed_text, get_default_backend

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://menir-db:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "menir123")

def main():
    print(f"Connecting to {NEO4J_URI}...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    backend = get_default_backend()
    print(f"Using Embedding Backend: {backend.__class__.__name__} (dim={backend.dim})")
    
    # Select Documents without embeddings
    # Target existing Itaú docs (from previous step)
    # They were :Document, not :DocumentChunk in previous script.
    # In Menir Schema, Documents usually have embeddings OR are chunked.
    # For this exercise, we embed the Document node directly.
    
    query_fetch = """
    MATCH (d:Document)
    WHERE d.project = 'Itaú' AND d.embedding IS NULL
    RETURN d.id AS id, d.text AS text
    """
    
    with driver.session() as session:
        result = list(session.run(query_fetch))
        print(f"Found {len(result)} documents to embed.")
        
        for record in result:
            doc_id = record["id"]
            text = record["text"]
            
            try:
                print(f"Embedding {doc_id}...")
                vector = embed_text(text)
                
                # Update
                session.run("""
                MATCH (d:Document {id: $id})
                SET d.embedding = $vector, d.embedding_model = $model
                """, id=doc_id, vector=vector, model=backend.__class__.__name__)
                
                # Also ensure Vector Index exists?
                # Usually created once. For now, just set property.
                
                print(f"Updated {doc_id}.")
                time.sleep(0.5) # Rate limit
            except Exception as e:
                print(f"Failed to embed {doc_id}: {e}")
                
    driver.close()
    print("Embedding Complete.")

if __name__ == "__main__":
    main()
