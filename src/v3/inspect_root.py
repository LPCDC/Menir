from src.v3.menir_bridge import MenirBridge
from src.v3.tenant_middleware import current_tenant_id
import pprint

def inspect_luiz():
    bridge = MenirBridge()
    with bridge.driver.session() as session:
        token = current_tenant_id.set("root_admin")
        try:
            print("\n----- LUIZ'S ROOT PROFILE -----")
            # Get properties
            res_node = session.run("MATCH (p:Person:Root {name: 'Luiz'}) RETURN properties(p) as props").single()
            if res_node:
                print("\n[PROPERTIES]")
                pprint.pprint(res_node["props"])
            else:
                print("Luiz node not found.")
                return

            # Get outgoing relationships
            print("\n[RELATIONSHIPS]")
            res_rels = session.run("""
            MATCH (luiz:Person:Root {name: 'Luiz'})-[r]->(dest)
            RETURN type(r) as rel_type, properties(r) as rel_props, labels(dest) as dest_labels, dest.name as dest_name
            ORDER BY type(r), dest.name
            """).data()
            
            for rel in res_rels:
                labels = ":".join(rel["dest_labels"])
                print(f"- [:{rel['rel_type']}] -> ({labels} {{name: '{rel['dest_name']}'}})")
                if rel["rel_props"]:
                    for k, v in rel["rel_props"].items():
                        print(f"    └─ {k}: {v}")
            
            print(f"\nTotal connections: {len(res_rels)}\n")

        finally:
            current_tenant_id.reset(token)
            
    bridge.close()

if __name__ == "__main__":
    inspect_luiz()
