
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv(override=True)

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER", "neo4j")
PID = os.getenv("NEO4J_PASSWORD")

print(f"Counting Nodes in: {URI}...")

try:
    driver = GraphDatabase.driver(URI, auth=(USER, PID))
    with driver.session() as session:
        count = session.run("MATCH (n) RETURN count(n) as c").single()['c']
        print(f"📊 TOTAL NODES: {count}")
        
        # Breakdown by Label
        res = session.run("MATCH (n) RETURN labels(n)[0] as lbl, count(n) as c ORDER BY c DESC")
        for r in res:
            print(f"   - {r['lbl']}: {r['c']}")
            
    driver.close()
except Exception as e:
    print(f"❌ ERROR: {e}")
