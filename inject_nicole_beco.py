import asyncio
import logging
from src.v3.core.neo4j_pool import get_shared_driver
from src.v3.core.embedding_service import EmbeddingService
from src.v3.core.schemas.personal import PersonNode

logging.basicConfig(level=logging.INFO)

async def main():
    driver = get_shared_driver()
    node = PersonNode(uid="nicole-beco-uuid-1", project="BECO", name="Nicole", role_or_context="Diretora Financeira Fiduciary")
    
    with driver.session() as session:
        session.run(
            "MERGE (p:PersonNode:`BECO` {uid: $uid}) SET p.name=$n, p.role_or_context=$r",
            uid=node.uid, n=node.name, r=node.role_or_context
        )
        
    text_embed = f"{node.name} {node.role_or_context}"
    await EmbeddingService.embed_and_persist(node.uid, text_embed, "PersonNode", "BECO")
    print("✅ Injected Nicole in BECO!")

asyncio.run(main())
