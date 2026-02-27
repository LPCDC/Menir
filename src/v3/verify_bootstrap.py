import os
from neo4j import GraphDatabase

# Explicitly set the Cloud credentials that worked
URI = "neo4j+s://e09bc76e.databases.neo4j.io"
AUTH = ("neo4j", "xG9QQS6hyuevf8DBhzBey5MqjDgPrdkYqniAkRpTEIY")

def verify():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    try:
        driver.verify_connectivity()
        print(f"Connected to {URI}")
        
        query = "MATCH (n:SystemEvent {name: 'MenirEngineerOnline'}) RETURN n, elementId(n) as id"
        with driver.session() as session:
            result = session.run(query).data()
            
        if result:
            print("✅ SUCCESSO: Node Found!")
            print(result)
        else:
            print("❌ FAILURE: Node NOT found.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    verify()
