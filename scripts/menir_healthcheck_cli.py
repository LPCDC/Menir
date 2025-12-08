#!/usr/bin/env python3
"""
Health check simples para Menir (conexão com Neo4j + verificação básica).
"""

import os
import sys
from neo4j import GraphDatabase, basic_auth

def main():
    uri  = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    pwd  = os.getenv("NEO4J_PWD")

    if not all([uri, user, pwd]):
        print("ERRO: variáveis de ambiente NEO4J_URI / NEO4J_USER / NEO4J_PWD não definidas.")
        sys.exit(1)

    try:
        driver = GraphDatabase.driver(uri, auth=basic_auth(user, pwd))
        # verifica conectividade imediatamente
        driver.verify_connectivity()
        with driver.session() as session:
            result = session.run("RETURN 1 AS ok LIMIT 1").single()
            print("[OK] Conexão com Neo4j verificada — resultado:", result["ok"])
        driver.close()
    except Exception as e:
        print(f"[ERRO] Falha ao conectar/consultar Neo4j: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
