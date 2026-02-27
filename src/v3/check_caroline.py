from src.v3.menir_bridge import MenirBridge

bridge = MenirBridge()
with bridge.driver.session() as session:
    print("--- CAROLINE INSPECTION ---")
    result = session.run("MATCH (p:Person) WHERE p.name CONTAINS 'Caroline' RETURN p.name, labels(p), p.context")
    for record in result:
        print(f"👤 Name: {record['p.name']} | Labels: {record['labels(p)']} | Context: {record.get('p.context', 'N/A')}")
        
bridge.close()
