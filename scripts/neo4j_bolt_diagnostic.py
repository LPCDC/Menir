#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo4j Bolt connection diagnostic.

Provides step-by-step diagnostics:
1. Driver creation
2. Connectivity verification
3. Trivial query execution

Environment:
  NEO4J_URI   - Bolt URI (default: bolt://localhost:7687)
  NEO4J_USER  - Username (default: neo4j)
  NEO4J_PWD   - Password (default: empty)

Exit code:
  0 - all steps successful
  1 - connection or query failed
"""

import os
import sys
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError, Neo4jError

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PWD = os.getenv("NEO4J_PWD", "")


def attempt_connect():
    """Attempt connection with diagnostic output."""
    try:
        driver = GraphDatabase.driver(URI, auth=(USER, PWD))
        print("[1] driver criado")
        driver.verify_connectivity()
        print("[2] verify_connectivity ok")
    except (ServiceUnavailable, AuthError, Neo4jError) as e:
        print("[ERROR] Não conseguiu conectar ao Bolt:", type(e).__name__, "-", e)
        return False

    try:
        with driver.session() as s:
            result = s.run("RETURN 1 AS v").single()
            val = result["v"] if result else None
            print("[3] Query trivial executada, retornou:", val)
    except Neo4jError as e:
        print("[ERROR] Erro ao executar query trivial:", type(e).__name__, "-", e)
        return False
    finally:
        driver.close()

    print("✅ Conexão Bolt + transação: OK")
    return True


if __name__ == "__main__":
    ok = attempt_connect()
    sys.exit(0 if ok else 1)
