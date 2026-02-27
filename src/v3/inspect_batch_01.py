from src.v3.menir_bridge import MenirBridge
from src.v3.tenant_middleware import current_tenant_id

def inspect_advanced_graph():
    bridge = MenirBridge()
    with bridge.driver.session() as session:
        token = current_tenant_id.set("root_admin")
        try:
            print("\n----- 🗓️ TEMPORAL EVENTS -----")
            ev_res = session.run("""
            MATCH (e:Event)
            OPTIONAL MATCH (e)-[:OCCURRED_IN]->(y:Year)
            OPTIONAL MATCH (p:Person)-[r]->(e)
            RETURN e.name as event, y.value as year, type(r) as participation, p.name as person
            ORDER BY e.name
            """).data()
            for r in ev_res:
                yr = f"({r['year']})" if r['year'] else "(No Year)"
                print(f"- Event: '{r['event']}' {yr}")
                if r['person']:
                    print(f"    └─ {r['person']} [:{r['participation']}]")

            print("\n----- 🧠 SKOS CONCEPTS -----")
            concept_res = session.run("""
            MATCH (c:Concept)
            OPTIONAL MATCH (c)-[r:BROADER|NARROWER]->(other:Concept|Document)
            RETURN c.name as concept, type(r) as rel, labels(other)[0] as other_label, other.name as other_name
            ORDER BY c.name
            """).data()
            
            seen_concepts = set()
            for r in concept_res:
                c = r['concept']
                if c not in seen_concepts:
                    print(f"- {c}")
                    seen_concepts.add(c)
                if r['rel']:
                    print(f"    └─ [:{r['rel']}] -> {r['other_label']} '{r['other_name']}'")

            print("\n----- 📜 PROVENANCE (PROV-O) -----")
            prov_res = session.run("""
            MATCH (d:Document)
            OPTIONAL MATCH (d)-[:WAS_DERIVED_FROM]->(e:Event)
            OPTIONAL MATCH (d)-[:WAS_ATTRIBUTED_TO]->(p:Person)
            RETURN d.name as doc, e.name as src_event, p.name as author
            """).data()
            for r in prov_res:
                print(f"- Document: '{r['doc']}'")
                if r['src_event']: print(f"    └─ DERIVED FROM: Event '{r['src_event']}'")
                if r['author']: print(f"    └─ ATTRIBUTED TO: Person '{r['author']}'")

        finally:
            current_tenant_id.reset(token)
            
    bridge.close()

if __name__ == "__main__":
    inspect_advanced_graph()
