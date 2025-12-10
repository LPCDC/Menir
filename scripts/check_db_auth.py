
import os
import sys
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Force load from .env in current directory
load_dotenv()

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "menir123")

print(f"🔍 EXTRACTED CONFIG:")
print(f"   URI: {uri}")
print(f"   USER: {user}")
print(f"   PASSWORD: {password[:5]}... (Len: {len(password) if password else 0})")

print("\n🔌 ATTEMPTING CONNECTION...")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    print("✅ CONNECTION SUCCESSFUL!")
    print("   The credentials in .env are VALID.")
    
    with driver.session() as session:
        result = session.run("RETURN 'Neo4j is Alive' AS status").single()
        print(f"   DB Response: {result['status']}")
        
    driver.close()
    sys.exit(0)
    
except Exception as e:
    print("❌ CONNECTION FAILED")
    print(f"   Error Type: {type(e).__name__}")
    print(f"   Message: {e}")
    sys.exit(1)
