#!/usr/bin/env python3
"""
test_neo4j_connection.py — Quick Neo4j connectivity test.
Useful for verifying connection before running other tools.
"""

import os
import sys
from neo4j import GraphDatabase

def test_connection():
    """Test Neo4j connection with environment variables."""
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    
    if not password:
        print("❌ NEO4J_PASSWORD not set")
        return False
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        print(f"✅ Conexão com Neo4j OK")
        print(f"   URI: {uri}")
        print(f"   User: {user}")
        
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            if result.single():
                print("✅ Query execution OK")
        
        driver.close()
        return True
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
