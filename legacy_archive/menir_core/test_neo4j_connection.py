from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "menir123")

driver = GraphDatabase.driver(uri, auth=(user, password))

def test_connection(tx):
    result = tx.run("RETURN 'Conexao Menir–Neo4j OK' AS msg")
    return result.single()["msg"]

if __name__ == "__main__":
    try:
        with driver.session() as session:
            msg = session.execute_read(test_connection)
            print("✅", msg)
    finally:
        driver.close()
