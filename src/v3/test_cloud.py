
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Force reload to get new .env values
load_dotenv(override=True)

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER", "neo4j")
PID = os.getenv("NEO4J_PASSWORD")

print(f"Testing Connection to: {URI}")
print(f"User: {USER}")

try:
    driver = GraphDatabase.driver(URI, auth=(USER, PID))
    with driver.session() as session:
        result = session.run("RETURN 'Cloud Connection Successful' as msg").single()
        print(f"✅ SUCCESS: {result['msg']}")
        
        # Check if database is empty (since it's new)
        count = session.run("MATCH (n) RETURN count(n) as c").single()['c']
        print(f"📊 Current Node Count: {count}")
        
    driver.close()
except Exception as e:
    print(f"❌ CONNECTION FAILED: {e}")
