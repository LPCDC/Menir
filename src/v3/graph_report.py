
from src.v3.menir_bridge import MenirBridge

def report():
    bridge = MenirBridge()
    with bridge.driver.session() as session:
        print("\n📊 --- MENIR GRAPH REPORT --- 📊")
        
        # 1. Counts by Label
        res_labels = session.run("MATCH (n) RETURN labels(n) as lbl, count(*) as c ORDER BY c DESC").data()
        print("\n[Node Counts]")
        for r in res_labels:
            print(f"- {r['lbl']}: {r['c']}")
            
        # 1.5. Index Status
        print("\n[Index Status]")
        res_idx = session.run("SHOW INDEXES YIELD name, type, state").data()
        for i in res_idx:
            print(f"- {i['name']} ({i['type']}): {i['state']}")
            
        # 2. Counts by Rel Type
        res_rels = session.run("MATCH ()-[r]->() RETURN type(r) as t, count(*) as c ORDER BY c DESC").data()
        print("\n[Relationship Counts]")
        for r in res_rels:
            print(f"- {r['t']}: {r['c']}")
            
        # 3. Daniella's Subgraph
        print("\n[Daniella Badinni Analysis]")
        res_dani = session.run("MATCH (p:Person {name: 'Daniella Badinni'}) RETURN p.uid, p.project").single()
        if not res_dani:
            print("❌ Person 'Daniella Badinni' NOT FOUND.")
        else:
            print(f"✅ Found Daniella (Project: {res_dani['p.project']})")
            
            # Check Connections
            res_conns = session.run("""
            MATCH (p:Person {name: 'Daniella Badinni'})-[r]->(n)
            RETURN type(r) as rel, labels(n) as target_labels, n.name as target_name
            """).data()
            
            if not res_conns:
                print("⚠️ Daniella is an ISOLATED NODE (No outgoing connections).")
            else:
                for c in res_conns:
                    print(f"  └─[:{c['rel']}]-> {c['target_labels']} ({c.get('target_name', 'No Name')})")

        # 4. Hybrid Status
        print("\n[Hybrid Engine Status]")
        res_hybrid = session.run("""
        MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
        RETURN d.filename as doc, count(c) as chunks
        """).data()
        
        if not res_hybrid:
            print("⚠️ No Hybrid Documents found (Vector space empty).")
        else:
            for h in res_hybrid:
                print(f"  📄 {h['doc']}: {h['chunks']} Chunks")

    bridge.close()

if __name__ == "__main__":
    report()
