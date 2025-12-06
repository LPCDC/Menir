#!/usr/bin/env python3
import os
from neo4j import GraphDatabase, exceptions

# Configurações da Aura (exportar antes de rodar)
AURA_URI   = os.getenv("NEO4J_AURA_URI")
AURA_USER  = os.getenv("NEO4J_AURA_USER")
AURA_PASS  = os.getenv("NEO4J_AURA_PASSWORD")

LOCAL_URI  = os.getenv("NEO4J_URI", "bolt://localhost:7687")
LOCAL_USER = os.getenv("NEO4J_USER", "neo4j")
LOCAL_PASS = os.getenv("NEO4J_PASSWORD", "menir123")

# Conectores
driver_local = GraphDatabase.driver(LOCAL_URI, auth=(LOCAL_USER, LOCAL_PASS))
driver_aura  = GraphDatabase.driver(AURA_URI,  auth=(AURA_USER, AURA_PASS))

def fetch_all(tx):
    """Retorna todos nós com suas labels, props e relações (rels armazenadas separadamente)."""
    q = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n, labels(n) AS labels, collect({rel_type: type(r), target_id: m.id, props: properties(r)}) AS rels
    """
    return list(tx.run(q))

def ingest_node_and_rels(aura_session, labels, props, node_id, rels):
    aura_session.run(
        f"MERGE (x:{':'.join(labels)} {{id: $id}}) "
        "SET x += $props",
        id=node_id,
        props=props
    )
    for rel in rels:
        aura_session.run(
            f"MATCH (src {{id: $src}}), (dst {{id: $dst}}) "
            f"MERGE (src)-[r:{rel['rel_type']}]->(dst) "
            "SET r += $props",
            src=node_id,
            dst=rel.get("target_id"),
            props=rel.get("props", {})
        )

def migrate():
    with driver_local.session() as s_local, driver_aura.session() as s_aura:
        all_nodes = s_local.execute_read(fetch_all)
        for record in all_nodes:
            node = record["n"]
            labels = record["labels"]
            props  = dict(node)
            node_id = props.get("id") or props.get("uuid") or node.id  # ajuste conforme sua modelagem
            rels  = record["rels"]
            ingest_node_and_rels(s_aura, labels, props, node_id, rels)

    print("✅ Migração incremental concluída.")

if __name__ == "__main__":
    migrate()
