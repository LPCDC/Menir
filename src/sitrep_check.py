import os
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase

def check_ricardo():
    print("\n🧟 CHECAGEM DE ZUMBIS (Ricardo):")
    load_dotenv()
    uri = os.getenv('NEO4J_URI')
    user = os.getenv('NEO4J_USERNAME', 'neo4j')
    pwd = os.getenv('NEO4J_PASSWORD')

    if not uri or not pwd:
        print('❌ SKIPPING: Credentials missing in .env')
        return

    try:
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        with driver.session() as session:
            query = 'MATCH (n:Person {name: "Ricardo"}) RETURN count(n) as count'
            res = session.run(query)
            count = res.single()[0]
            print(f"Ricardo Nodes Found: {count}")
        driver.close()
    except Exception as e:
        print(f'❌ ERRO AO CONECTAR NO NEO4J: {e}')

def check_keys():
    print("\n🔑 VERIFICAÇÃO DE CHAVES (Ambiente):")
    load_dotenv()
    gemini_key = os.getenv("GEMINI_API_KEY")
    neo4j_pass = os.getenv("NEO4J_PASSWORD")
    print(f'GEMINI: {bool(gemini_key)}, NEO4J: {bool(neo4j_pass)}')

if __name__ == "__main__":
    check_ricardo()
    check_keys()
