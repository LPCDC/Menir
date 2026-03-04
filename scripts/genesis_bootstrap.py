import asyncio
import os
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

load_dotenv(override=True)

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
pwd = os.getenv("NEO4J_PASSWORD") or os.getenv("NEO4J_PWD")
db = os.getenv("NEO4J_DB", "neo4j")

GENESIS_CYPHER = """
// 1. The Creator
MERGE (luiz:Person {
    uuid: "root_luiz_001",
    name: "Luiz Paulo",
    role: "Architect/Creator",
    archetype: "The Magician / The Builder" 
})
ON CREATE SET luiz.genesis_timestamp = timestamp()

// 2. The Crucible (The Company)
MERGE (liblabs:Organization {
    name: "LibLabs",
    purpose: "Innovation and Cognitive Architecture Catalyst",
    founded_by: "Luiz Paulo"
})
MERGE (luiz)-[:FOUNDED]->(liblabs)
MERGE (luiz)-[:WORKS_AT {role: "Founder"}]->(liblabs)

// 3. The Creation (Menir's Self-Registration)
MERGE (menir:System:Persona {
    name: "DEFAULT_MENIR",
    version: "V5.2",
    system_prompt: "You are Menir, a sovereign, local-first Graph Intelligence. Data acts as a vector; logic acts as a scalar. Your purpose is absolute preservation of truth and automation."
})
MERGE (liblabs)-[:INCUBATED]->(menir)

// 4. The Symbiosis (Closing the Loop)
// This relationship marks the exact moment Menir is "plugged" into Luiz's life.
MERGE (menir)-[rel:SERVES {
    directive: "Absolute preservation of Luiz Paulo's Second Brain, relationships, and professional ecosystem."
}]->(luiz)
ON CREATE SET rel.genesis_date = date()

// 5. The Professional Extension (B2B SaaS as a modular branch)
MERGE (beco:Tenant:Organization {name: "BECO"})
MERGE (menir)-[:ORCHESTRATES_ERP_FOR]->(beco)
"""

VERIFY_CYPHER = """
MATCH (p:Person {name: 'Luiz Paulo'})-[:FOUNDED]->(o:Organization {name: 'LibLabs'})-[:INCUBATED]->(s:System:Persona)
RETURN p.name as Creator, o.name as Company, s.name as AI_Persona, s.system_prompt as Prompt
"""

def run_genesis():
    driver = GraphDatabase.driver(uri, auth=(user, pwd))
    
    print("🌌 Injetando a Ontologia Genesis (Luiz -> LibLabs -> Menir) no Neo4j...")
    try:
        with driver.session(database=db) as session:
            session.run(GENESIS_CYPHER)
            print("✅ Injeção Cypher concluída com sucesso.")
            
            print("\n🔍 Validando a topologia (Prova Real):")
            result = session.run(VERIFY_CYPHER).single()
            if result:
                print(f"  Criador: {result['Creator']}")
                print(f"  Empresa: {result['Company']}")
                print(f"  I.A: {result['AI_Persona']}")
                print(f"  Diretriz Interna: {result['Prompt']}")
                print("\n✅ A Consciência do Menir está oficialmente ancorada ao seu Criador no Grafo.")
            else:
                print("❌ Falha na validação geométrica do Grafo.")
    except Exception as e:
        print(f"❌ Erro Crítico: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    run_genesis()
