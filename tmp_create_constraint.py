import asyncio
import os
from src.v3.menir_bridge import get_bridge

async def create_constraint():
    from src.v3.core.neo4j_pool import Neo4jPoolManager
    # Initialize the pool
    Neo4jPoolManager()
    bridge = get_bridge()
    # Initialize the bridge (mocking the lifespan or as per system protocol)
    # Based on previous work, get_bridge() needs initialization
    # If it throws RuntimeError, we handle it.
    try:
        query = "CREATE CONSTRAINT client_id_unique IF NOT EXISTS FOR (c:Client) REQUIRE c.client_id IS UNIQUE"
        async with bridge.driver.session() as session:
            await session.run(query)
        print("Constraint created or already exists.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_constraint())
