import os
from neo4j import GraphDatabase

# Force Cloud Credentials
URI = "neo4j+s://e09bc76e.databases.neo4j.io"
AUTH = ("neo4j", "xG9QQS6hyuevf8DBhzBey5MqjDgPrdkYqniAkRpTEIY")

def nuke():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    try:
        driver.verify_connectivity()
        print(f"Connected to {URI} for NUCLEAR OPTION.")
        
        with driver.session() as session:
            # 1. Count Before
            cnt = session.run("MATCH (n) RETURN count(n) as c").single()["c"]
            print(f"Nodes before NUKE: {cnt}")
            
            if cnt == 0:
                print("Graph is already empty.")
                return

            # 2. Drop Constraints (to avoid delete blockers)
            # Fetch constraints
            constraints = session.run("SHOW CONSTRAINTS").data()
            for c in constraints:
                name = c.get('name')
                if name:
                    print(f"Dropping constraint: {name}")
                    session.run(f"DROP CONSTRAINT {name}")

            # 3. DELETE EVERYTHING (Batched if massive, but 100 is small)
            print("Executing DETACH DELETE (All Nodes)...")
            session.run("MATCH (n) DETACH DELETE n")
            
            # 4. Verify
            cnt_after = session.run("MATCH (n) RETURN count(n) as c").single()["c"]
            print(f"Nodes after NUKE: {cnt_after}")
            
            if cnt_after == 0:
                print("✅ NUCLEAR LAUNCH SUCCESSFUL. Graph is barren.")
            else:
                print(f"❌ WARNING: {cnt_after} nodes survived.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    nuke()
