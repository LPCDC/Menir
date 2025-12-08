#!/usr/bin/env bash
# neo4j_bolt_check.sh
#
# Test Neo4j Bolt connectivity with configurable environment variables.
#
# Environment:
#   NEO4J_URI   - Bolt URI (default: bolt://localhost:7687)
#   NEO4J_USER  - Username (default: neo4j)
#   NEO4J_PWD   - Password (default: empty)
#
# Exit code:
#   0 - connected successfully
#   1 - connection failed

URI="${NEO4J_URI:-bolt://localhost:7687}"
USER="${NEO4J_USER:-neo4j}"
PWD="${NEO4J_PWD:-}"

echo "→ Testando conexão Bolt Neo4j"
echo "URI: $URI  USER: $USER"
echo ""

python3 - << 'PYCODE'
import os
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable, AuthError

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
pwd  = os.getenv("NEO4J_PWD", "")

def test_conn():
    try:
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        driver.verify_connectivity()
        with driver.session() as s:
            s.run("RETURN 1").single()
        print("✅ Conexão Bolt FUNCIONANDO — Bolt OK")
        return 0
    except (ServiceUnavailable, AuthError, Neo4jError) as e:
        print("❌ Falha na conexão Bolt:", type(e).__name__, "-", str(e))
        return 1
    finally:
        try:
            driver.close()
        except:
            pass

if __name__ == "__main__":
    import sys
    exit_code = test_conn()
    sys.exit(exit_code)
PYCODE
