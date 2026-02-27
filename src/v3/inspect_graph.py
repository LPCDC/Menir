from src.v3.menir_bridge import MenirBridge

bridge = MenirBridge()
with bridge.driver.session() as session:
    print("--- DOCUMENTOS INGERIDOS ---")
    result = session.run("MATCH (d:Document) RETURN d.filename, d.ingested_at")
    for record in result:
        print(f"📄 {record['d.filename']} (Em: {record['d.ingested_at']})")
        
    print("\n--- ESTATÍSTICAS ---")
    counts = session.run("MATCH (n) RETURN labels(n) as lbl, count(*) as c").data()
    for row in counts:
        print(f"{row['lbl']}: {row['c']}")
        
    print("\n--- CAPÍTULO 2? ---")
    chap2 = session.run("MATCH (d:Document) WHERE d.filename CONTAINS '2' RETURN d.filename").data()
    if chap2:
        print(f"⚠️ Capítulo 2 detectado: {chap2}")
    else:
        print("✅ Capítulo 2 NÃO encontrado.")
        
bridge.close()
