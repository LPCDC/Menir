#!/usr/bin/env python3
"""
sanity_neo4j_full.py — Verifica conexão com Neo4j e realiza um teste simples de leitura/escrita.
Configurações via variáveis de ambiente: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD.
"""

import os
import sys
import logging
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError, Neo4jError

# Setup de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def get_env_var(key, default=None):
    v = os.getenv(key)
    if not v:
        return default
    return v

def test_connection(uri, user, password):
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        logging.info("✅ Conexão com Neo4j estabelecida com sucesso.")
        return driver
    except AuthError as e:
        logging.error("❌ Falha de autenticação: %s", e)
    except ServiceUnavailable as e:
        logging.error("❌ Serviço indisponível / sem conexão: %s", e)
    except Exception as e:
        logging.error("❌ Erro inesperado na conexão: %s", e)
    return None

def test_read_write(driver):
    TEST_LABEL = "SanityTest"
    TEST_PROP = {"check": "ok", "timestamp": logging.Formatter().formatTime(logging.LogRecord("", "", "", "", "", None, None))}
    session = None
    try:
        session = driver.session()
        # Criar um nó temporário
        create_cypher = (
            f"CREATE (n:{TEST_LABEL} $props) RETURN id(n) AS id"
        )
        result = session.run(create_cypher, props=TEST_PROP)
        rec = result.single()
        if rec is None:
            logging.warning("⚠️ Não foi possível criar nó de teste.")
            return False
        node_id = rec["id"]
        logging.info("Criado nó de teste com id %s", node_id)

        # Ler esse nó
        read_cypher = (
            f"MATCH (n:{TEST_LABEL}) WHERE id(n) = $id RETURN n"
        )
        result2 = session.run(read_cypher, id=node_id)
        rec2 = result2.single()
        if rec2 is None:
            logging.warning("⚠️ Não foi possível ler nó de teste criado.")
            return False
        logging.info("Leitura confirmada do nó de teste.")

        # Deletar o nó de teste
        delete_cypher = (
            f"MATCH (n:{TEST_LABEL}) WHERE id(n) = $id DETACH DELETE n"
        )
        session.run(delete_cypher, id=node_id)
        logging.info("Nó de teste removido; limpeza OK.")

        return True
    except Neo4jError as e:
        logging.error("❌ Erro Neo4j durante read/write: %s", e)
    except Exception as e:
        logging.error("❌ Erro inesperado durante read/write: %s", e)
    finally:
        if session:
            session.close()
    return False

def main():
    uri = get_env_var("NEO4J_URI", "bolt://localhost:7687")
    user = get_env_var("NEO4J_USER", "neo4j")
    password = get_env_var("NEO4J_PASSWORD", None)

    if password is None:
        logging.error("Variável de ambiente NEO4J_PASSWORD não definida. Abortando.")
        sys.exit(1)

    driver = test_connection(uri, user, password)
    if not driver:
        sys.exit(1)

    success = test_read_write(driver)
    if success:
        logging.info("✅ Teste completo de leitura/escrita no Neo4j ok.")
    else:
        logging.warning("⚠️ Teste de leitura/escrita falhou — revisar logs acima.")

    driver.close()

if __name__ == "__main__":
    main()
