import os
import sys
from decimal import Decimal

# Incluir diretorio raiz no path
sys.path.append(os.getcwd())

from src.v3.meta_cognition import MenirOntologyManager

def run_layer_1():
    print("--- LAYER 1 DIAGNOSTIC: NEO4J & ISOLATION ---")
    ontology = MenirOntologyManager()
    
    with ontology.driver.session() as session:
        # 1. Conectividade e Nós Raiz
        print("\n[V1] Checking Connectivity and Root Nodes...")
        roots = session.run("""
            MATCH (m:Menir {uid: 'MENIR_CORE'})
            MATCH (u:User {uid: 'luiz'})
            RETURN m, u
        """).single()
        
        if roots:
            print("✅ Root nodes (:Menir {uid:'MENIR_CORE'}) and (:User {uid:'luiz'}) found.")
        else:
            print("❌ Root nodes NOT found or incomplete.")

        # 2. Isolamento Galvânico (BECO <-> SANTOS)
        print("\n[V2] Checking Galvanic Isolation (BECO <-> SANTOS)...")
        # Conta qualquer aresta entre nós de tenants diferentes
        cross_tenant = session.run("""
            MATCH (n:BECO)-[r]-(m:SANTOS)
            RETURN count(r) as cross_count
        """).single()
        
        count = cross_tenant["cross_count"]
        if count == 0:
            print("✅ Isolation confirmed: 0 relationships found between BECO and SANTOS.")
        else:
            print(f"❌ VIOLATION: {count} relationships found between BECO and SANTOS nodes!")

        # 3. Contagem de Nós BECO
        print("\n[V3] BECO Node Counts:")
        counts = session.run("""
            MATCH (n:BECO)
            WITH labels(n) as lbls, count(n) as cnt
            WHERE any(l in lbls WHERE l IN ['Invoice', 'Client', 'Transaction', 'QuarantineItem'])
            RETURN lbls, cnt
        """)
        
        found_labels = {}
        for record in counts:
            for l in record["lbls"]:
                if l in ['Invoice', 'Client', 'Transaction', 'QuarantineItem']:
                    found_labels[l] = record["cnt"]
        
        for lbl in ['Invoice', 'Client', 'Transaction', 'QuarantineItem']:
             print(f"- {lbl}: {found_labels.get(lbl, 0)}")

    ontology.close()
    print("\n--- LAYER 1 DIAGNOSTIC COMPLETE ---")

if __name__ == "__main__":
    run_layer_1()
