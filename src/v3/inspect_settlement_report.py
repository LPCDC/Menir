from src.v3.menir_bridge import MenirBridge
from src.v3.tenant_middleware import current_tenant_id

def inspect_settlement():
    bridge = MenirBridge()
    with bridge.driver.session() as session:
        token = current_tenant_id.set("root_admin")
        try:
            print("\n----- ⚖️  LEGAL & FINANCIAL SETTLEMENT -----")
            
            res = session.run("""
            MATCH (ev:Event {name: 'Quitação Integral de Dívida'})
            OPTIONAL MATCH (ev)-[:OCCURRED_ON]->(d:Day)<-[:HAS_DAY]-(m:Month)<-[:HAS_MONTH]-(y:Year)
            OPTIONAL MATCH (p:Person)-[r:PARTICIPATED_IN]->(ev)
            OPTIONAL MATCH (ev)-[:PRODUCED]->(doc:Document)
            OPTIONAL MATCH (ev)-[:RESOLVED]->(ev_old:Event)
            RETURN ev.name as event_name, ev.total_settled_brl as total, 
                   y.value as year, m.value as month, d.value as day,
                   p.name as person, r.role as role, doc.name as doc_name,
                   ev_old.name as old_event
            ORDER BY p.name
            """).data()

            if res:
                e = res[0]
                date_str = f"{e['day']}/{e['month']}/{e['year']}" if e['year'] else "Unknown Date"
                print(f"EVENT: {e['event_name']}")
                print(f"  └─ Date: {date_str}")
                print(f"  └─ Total Settled: R$ {e['total']}")
                
                if e['doc_name']:
                    print(f"  └─ Produced Document: '{e['doc_name']}'")
                if e['old_event']:
                    print(f"  └─ Resolves Event: '{e['old_event']}'")
                    
                print("\nPARTICIPANTS:")
                for r in res:
                    if r['person']:
                        print(f"  - {r['person']} (Role: {r['role']})")
            
        finally:
            current_tenant_id.reset(token)
            
    bridge.close()

if __name__ == "__main__":
    inspect_settlement()
