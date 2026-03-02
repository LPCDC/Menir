import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

def check_neo4j_connection():
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "menir123")
    uris = [os.getenv("NEO4J_URI"), "neo4j://localhost:7687", "neo4j://127.0.0.1:7687"]
    
    for uri in uris:
        if not uri: continue
        try:
            driver = GraphDatabase.driver(uri, auth=(user, password))
            driver.verify_connectivity()
            return driver
        except Exception:
            continue
    return None
