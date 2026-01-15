from google import genai
from neo4j import GraphDatabase

# --- PAINEL DE CONTROLE (SOLDADO) ---
MINHA_CHAVE_GOOGLE = "AIzaSyD2j29_NoR_g-9t3reeOeU0wCHGXbwxLeo" 
MINHA_SENHA_NEO4J = "menir123" 
# ------------------------------------

client = genai.Client(api_key=MINHA_CHAVE_GOOGLE)

def injetar_sinal_bruto():
    # Definindo os dados com MERGE absoluto para garantir a criação
    cypher_reset = """
    MERGE (l:Persona {name: 'Luiz', role: 'Root'})
    MERGE (n:Persona {name: 'Newton Pipoca', role: 'Amigo Virtual'})
    SET n.quality = 'Boa', n.price = 'Cara'
    MERGE (l)-[:FRIEND_OF]->(n)
    
    MERGE (d:Persona {name: 'Débora', role: 'Autora'})
    MERGE (l)-[:FRIEND_OF]->(d)
    
    MERGE (c:Character {name: 'Caroline'})
    MERGE (h:Character {name: 'Henry', gestation_weeks: 10})
    MERGE (c)-[:SISTER_OF]->(h)
    
    RETURN l, n, c, h
    """
    
    try:
        print("💉 Injetando sinal de força bruta no Neo4j...")
        with GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", MINHA_SENHA_NEO4J)) as driver:
            with driver.session() as session:
                result = session.run(cypher_reset)
                summary = result.consume()
                print(f"✅ GRAVAÇÃO REALIZADA: {summary.counters.nodes_created} nós criados.")
                
    except Exception as e:
        print(f"❌ Falha no sinal: {e}")

if __name__ == "__main__":
    injetar_sinal_bruto()