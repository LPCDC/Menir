import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from src.v3.core.neo4j_pool import get_shared_driver

async def main():
    driver = get_shared_driver()
    query = """
    MATCH (t:Tenant {name: "BECO"})-[:RECEIVED]->(i:Invoice)-[r:RECONCILED]->(tr:Transaction)
    MATCH (v:Vendor)-[:ISSUED]->(i)
    RETURN i, v
    LIMIT 1
    """
    with driver.session() as session:
        result = session.run(query)
        data = [rec.data() for rec in result]
    
    print(f"QUERY RESULT: {data}")

if __name__ == "__main__":
    asyncio.run(main())
