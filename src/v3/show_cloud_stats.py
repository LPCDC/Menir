
import os
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv(override=True)

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER", "neo4j")
PID = os.getenv("NEO4J_PASSWORD")

print(f"🔎 Inspecting Cloud Graph: {URI}...")

try:
    driver = GraphDatabase.driver(URI, auth=(USER, PID))
    with driver.session() as session:
        # 1. Total Count
        count = session.run("MATCH (n) RETURN count(n) as c").single()['c']
        print(f"\n📊 TOTAL NODES: {count}")
        
        # 2. Latest Documents
        print("\n📄 LATEST DOCUMENTS (Last 5):")
        res = session.run("""
            MATCH (d:Document) 
            RETURN d.filename as name, d.ingested_at as time, d.status as status
            ORDER BY d.ingested_at DESC LIMIT 5
        """)
        for r in res:
            print(f"   - {r['name']} ({r['status']}) @ {r['time']}")

        # 3. Vector Chunks
        print("\n🧠 VECTOR MEMORY:")
        chunk_count = session.run("MATCH (c:Chunk) RETURN count(c) as cc").single()['cc']
        print(f"   - Stored Chunks: {chunk_count}")
            
    driver.close()
except Exception as e:
    print(f"❌ ERROR: {e}")
