#!/usr/bin/env python3
"""
Health check simples para Menir (Neo4j + conectividade).
"""

import os
import sys
from neo4j import GraphDatabase, basic_auth

def main():
    uri  = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    pwd  = os.getenv("NEO4J_PWD")

    if not all([uri, user, pwd]):
        # Fallback for local development if not set, or just fail
        # For now, we fail as requested in the skeleton
        print("ERRO: variáveis de ambiente NEO4J_URI / NEO4J_USER / NEO4J_PWD não definidas.")
        print("Dica: Verifique se o arquivo .env existe e foi carregado.")
        sys.exit(1)

    try:
        driver = GraphDatabase.driver(uri, auth=basic_auth(user, pwd))
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) AS c").single()
            count = result["c"]
            print(f"[OK] Conectado ao Neo4j — nós totais: {count}")
        driver.close()
    except Exception as e:
        print(f"[ERRO] Falha ao conectar/consultar Neo4j: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
