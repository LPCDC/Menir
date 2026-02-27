from src.v3.menir_bridge import MenirBridge

bridge = MenirBridge()
with bridge.driver.session() as session:
    print("--- INSPECTOR GADGET ---")
    
    # Check for LibLabs
    print("\n[LibLabs Nodes]")
    res = session.run("MATCH (n {name: 'LibLabs'}) RETURN labels(n), n.role, n.type, elementId(n)")
    for r in res: print(r)
    
    # Check for Tivoli
    print("\n[Tivoli Nodes]")
    res = session.run("MATCH (n {name: 'Tivoli'}) RETURN labels(n), n.type, elementId(n)")
    for r in res: print(r)
    
    # Check for Menir
    print("\n[Menir Nodes]")
    res = session.run("MATCH (n {name: 'Menir'}) RETURN labels(n), elementId(n)")
    for r in res: print(r)
    
    # Check for Débora
    print("\n[Débora Nodes]")
    res = session.run("MATCH (n {name: 'Débora Vezzoli'}) RETURN labels(n), elementId(n)")
    for r in res: print(r)

    # Check Relationships
    print("\n[Weird Relationships]")
    query = """
    MATCH (a)-[r]->(b)
    WHERE a.name IN ['Menir', 'Débora Vezzoli', 'LibLabs', 'Luiz'] 
       OR b.name IN ['Tivoli', 'Menir', 'Débora Vezzoli', 'LibLabs']
    RETURN a.name, type(r), b.name, labels(b)
    """
    res = session.run(query)
    for r in res:
        print(f"({r['a.name']}) -[{r['type(r)']}]-> ({r['b.name']}) {r['labels(b)']}")

bridge.close()
