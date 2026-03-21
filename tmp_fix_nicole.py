import os
import sys

# Incluir diretorio raiz no path
sys.path.append(os.getcwd())

from src.v3.meta_cognition import MenirOntologyManager

def fix_nicole_ontology():
    print("--- TAREFA A: CORREÇÃO ONTOLÓGICA NICOLE ---")
    ontology = MenirOntologyManager()
    
    with ontology.driver.session() as session:
        # 1. Remover aresta violadora
        print("1. Removing isolation violation edge (REFERENCED_FROM)...")
        session.run("""
            MATCH (n:BECO {uid: 'nicole-beco-uuid-1'})-[r:REFERENCED_FROM]-(m:SANTOS {uid: '7246d7ca-d2af-4406-8261-471b0e7e9615'})
            DELETE r
        """)

        # 2. Criar Nó Raiz (:Person) e Vincular ao Usuário
        print("2. Mapping Root Person node (:Person {uid:'nicole-berra'}) and linking to :User {uid:'luiz'}...")
        session.run("""
            MERGE (p:Person {uid: 'nicole-berra'})
            SET p.name = 'Nicole Berra', p.role = 'afilhada'
            WITH p
            MATCH (u:User {uid: 'luiz'})
            MERGE (p)-[:BELONGS_TO_USER]->(u)
        """)

        # 3. Vincular Nó Raiz ao Contexto BECO
        print("3. Linking root to BECO context (:Person -> :PersonNode)...")
        session.run("""
            MATCH (p:Person {uid: 'nicole-berra'})
            MATCH (pn:BECO:PersonNode {uid: 'nicole-beco-uuid-1'})
            MERGE (p)-[r:HAS_ROLE {tenant: 'BECO', role: 'operadora'}]->(pn)
        """)

        # 4. Vincular Nó Raiz ao Contexto SANTOS
        print("4. Linking root to SANTOS context (:Person -> :PersonNode)...")
        session.run("""
            MATCH (p:Person {uid: 'nicole-berra'})
            MATCH (pn:SANTOS:PersonNode {uid: '7246d7ca-d2af-4406-8261-471b0e7e9615'})
            MERGE (p)-[r:KNOWN_BY {tenant: 'SANTOS', relation: 'afilhada'}]->(pn)
        """)

        print("\n--- TAREFA B: VERIFICAÇÃO DE ISOLAMENTO ---")
        cross_tenant = session.run("""
            MATCH (n:BECO)-[r]-(m:SANTOS)
            RETURN count(r) as cross_count
        """).single()
        
        count = cross_tenant["cross_count"]
        if count == 0:
            print("✅ Isolation RE-VERIFIED: 0 relationships found between BECO and SANTOS.")
        else:
            # Identificar o que sobrou
            leftover = session.run("""
                MATCH (n:BECO)-[r]-(m:SANTOS)
                RETURN type(r) as type, labels(n), labels(m)
            """).data()
            print(f"❌ STILL VIOLATING: {count} relationships left.")
            print(leftover)

    ontology.close()

if __name__ == "__main__":
    fix_nicole_ontology()
