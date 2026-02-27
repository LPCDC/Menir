import os
from neo4j import GraphDatabase

URI = "neo4j+s://e09bc76e.databases.neo4j.io"
AUTH = ("neo4j", "xG9QQS6hyuevf8DBhzBey5MqjDgPrdkYqniAkRpTEIY")

def debug():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    try:
        driver.verify_connectivity()
        print(f"Connected to {URI}")
        
        with driver.session() as session:
            # 1. Total Count
            cnt = session.run("MATCH (n) RETURN count(n) as c").single()["c"]
            print(f"Total Nodes: {cnt}")
            
            # 2. Check Proposal Logs
            logs = session.run("MATCH (l:ProposalLog) RETURN l ORDER BY l.applied_at DESC LIMIT 5").data()
            print(f"Proposal Logs Found: {len(logs)}")
            for Log in logs:
                print(f" - {Log['l']}")
                
            # 3. Check SystemEvent specific
            evt = session.run("MATCH (n:SystemEvent) RETURN n").data()
            print(f"SystemEvents Found: {len(evt)}")
            for e in evt:
                print(f" - {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    debug()
