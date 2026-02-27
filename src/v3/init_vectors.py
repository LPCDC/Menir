
"""
Vector Index Initialization (Horizon 4)
Creates the required Vector Index in Neo4j for semantic search.
"""
from src.v3.menir_bridge import MenirBridge
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InitVectors")

def init_index():
    bridge = MenirBridge()
    
    with bridge.driver.session() as session:
        # 1. Drop old index if it has a different name
        logger.info("📡 Cleaning up legacy indices...")
        session.run("DROP INDEX menir_vectors IF EXISTS")
        
        # 2. Create Vector Index for Chunk nodes
        # Gemini text-embedding-004 uses 768 dimensions
        query = """
        CREATE VECTOR INDEX `chunk_embeddings` IF NOT EXISTS
        FOR (c:Chunk) ON (c.embedding)
        OPTIONS {indexConfig: {
         `vector.dimensions`: 768,
         `vector.similarity_function`: 'cosine'
        }}
        """
        logger.info("📡 Creating Vector Index 'chunk_embeddings' (Cosine, 768 dims)...")
        session.run(query)
        logger.info("✅ Index Creation Command Sent.")

    bridge.close()

if __name__ == "__main__":
    init_index()
