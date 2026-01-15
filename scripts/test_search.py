import sys
import os
import time

sys.path.append("/app")
from neo4j import GraphDatabase
from menir_core.embeddings import embed_text

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://menir-db:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "menir123")

def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    # Ensure Index
    with driver.session() as session:
        session.run("""
        CREATE VECTOR INDEX document_embeddings IF NOT EXISTS
        FOR (d:Document) ON (d.embedding)
        OPTIONS {indexConfig: {
          `vector.dimensions`: 768,
          `vector.similarity_function`: 'cosine'
        }}
        """)
        # Await index online? usually fast.
    
    query_text = "Compliance logs related to Joao Silva"
    print(f"Query: {query_text}")
    
    embedding = embed_text(query_text)
    
    with driver.session() as session:
        result = session.run("""
        CALL db.index.vector.queryNodes('document_embeddings', 10, $embedding)
        YIELD node, score
        RETURN node.text AS text, node.id AS id, score
        """, embedding=embedding)
        
        print(f"--- Search Results ---")
        found_target = False
        pii_leaked = False
        
        for record in result:
            text = record["text"]
            score = record["score"]
            doc_id = record["id"]
            
            print(f"[{score:.4f}] {doc_id}: {text}")
            
            if "[PESSOA_TERC_001]" in text:
                found_target = True
                print(">>> MATCH CONFIRMED: Found masked placeholder for Joao Silva.")
            
            if "Joao Silva" in text:
                pii_leaked = True
                print(">>> PRIVACY FAILURE: Raw PII found in text!")
                
    driver.close()

if __name__ == "__main__":
    main()
