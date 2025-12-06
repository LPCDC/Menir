#!/usr/bin/env bash
#
# finalize_menir_setup.sh — sanity check Neo4j + commit/push final + tag v10.4.1-bootstrap
# Uso: bash finalize_menir_setup.sh

set -e

echo "🚀 Iniciando sanity check Neo4j..."

# Configuração de variáveis (defaults)
NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-menir123}"

python3 - << 'PYCODE'
import os, sys
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError, Neo4jError

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "menir123")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    print("✅ Neo4j: conexão bolt OK —", uri)
    with driver.session() as s:
        rec = s.run("CALL dbms.components() YIELD name, versions, edition RETURN name, versions, edition").single()
        if rec:
            print(f"   ➤ Banco: {rec['name']}, versão(s): {rec['versions']}, edição: {rec.get('edition', 'unknown')}")
        else:
            print("⚠️ Aviso: dbms.components() retornou vazio — não confirmou versão/edição")
except AuthError as e:
    print("❌ Falha de autenticação Neo4j:", e)
    sys.exit(1)
except ServiceUnavailable as e:
    print("❌ Serviço Neo4j indisponível / conexão falhou:", e)
    sys.exit(1)
except Neo4jError as e:
    print("❌ Erro Neo4j:", e)
    sys.exit(1)
except Exception as e:
    print("❌ Erro inesperado:", e)
    sys.exit(1)
finally:
    try:
        driver.close()
    except:
        pass
PYCODE

echo "✅ Sanity check concluído com sucesso."

echo "📦 Preparando commit final + push + tag..."

git add .
git commit -m "bootstrap: finalize setup Neo4j + devcontainer/README fix"
git tag -a "v10.4.1-bootstrap" -m "Menir v10.4.1 bootstrap final commit"
git push
git push origin "v10.4.1-bootstrap"

echo "🔁 Setup finalizado — commit, push e tag v10.4.1-bootstrap criados."
