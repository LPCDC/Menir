from src.v3.menir_bridge import MenirBridge

bridge = MenirBridge()
with bridge.driver.session() as session:
    print("--- RENAMING FICTIONAL CAROLINE ---")
    # Match Caroline who is NOT the Real One
    query = """
    MATCH (p:Person {name: 'Caroline'})
    WHERE NOT p.context = 'Real World'
    SET p.name = 'Caroline Howell'
    RETURN p.name, p.context
    """
    result = session.run(query)
    for record in result:
        print(f"✅ Renamed to: {record['p.name']}")
        
bridge.close()
