#!/usr/bin/env python3
"""Query claims from the initialized graph."""
import os
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load .env from repo root
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))

with driver.session() as session:
    # Query claims related to Caroline
    result = session.run("""
        MATCH (c:Claim)
        WHERE c.subject = "Caroline"
        RETURN c.id, c.subject, c.predicate, c.object, c.status
    """)
    
    print("Claims for Caroline:")
    for record in result:
        print(f"  [{record['c.status']}] {record['c.subject']} {record['c.predicate']} {record['c.object']}")
        print(f"    ID: {record['c.id']}")
    
    # Query contradictions
    print("\nContradictions:")
    result = session.run("""
        MATCH (cl1:Claim)-[r:CONTRADICTS]->(cl2:Claim)
        RETURN cl1.id, cl1.object, cl2.id, cl2.object, r.severity
    """)
    
    for record in result:
        print(f"  {record['cl1.id']} ({record['cl1.object']}) -- CONTRADICTS[{record['r.severity']}] --> {record['cl2.id']} ({record['cl2.object']})")

driver.close()
