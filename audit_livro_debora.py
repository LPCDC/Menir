#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit script para grafo Livro Débora (Menir).

Calcula:
 - Quantidade de nós por label
 - Quantidade de relações por tipo
 - Relações entre personagens
 - Relações gerais no grafo (até limite)
"""

from neo4j import GraphDatabase, basic_auth
import os
import csv

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "menir123")
NEO4J_DB = os.getenv("NEO4J_DB", None)

auth = basic_auth(NEO4J_USER, NEO4J_PASSWORD)
driver = GraphDatabase.driver(NEO4J_URI, auth=auth)

def get_session():
    if NEO4J_DB:
        return driver.session(database=NEO4J_DB)
    return driver.session()

def count_nodes_by_label(tx):
    result = tx.run("""
        CALL db.labels() YIELD label
        CALL {
            WITH label
            MATCH (n)
            WHERE label IN labels(n)
            RETURN count(n) AS count
        }
        RETURN label, count
        ORDER BY count DESC
    """)
    return [(record["label"], record["count"]) for record in result]

def count_relations_by_type(tx):
    result = tx.run("""
        MATCH ()-[r]->()
        RETURN type(r) AS relType, count(r) AS cnt
        ORDER BY cnt DESC
    """)
    return [(record["relType"], record["cnt"]) for record in result]

def list_character_relations(tx):
    result = tx.run("""
        MATCH (c1:Character)-[r]-(c2:Character)
        RETURN c1.name AS from, type(r) AS relation, c2.name AS to
    """)
    return [(rec["from"], rec["relation"], rec["to"]) for rec in result]

def list_all_relations_sample(tx, limit=200):
    result = tx.run(f"""
        MATCH (n)-[r]-(m)
        RETURN labels(n) AS labelsN, n.id AS idN, type(r) AS rel, labels(m) AS labelsM, m.id AS idM
        LIMIT {limit}
    """)
    return [ (rec["labelsN"], rec["idN"], rec["rel"], rec["labelsM"], rec["idM"]) for rec in result]

def main():
    with get_session() as sess:
        print("=== NODE COUNTS BY LABEL ===")
        for label, cnt in sess.execute_read(count_nodes_by_label):
            print(f"{label}: {cnt}")
        print("\n=== RELATIONSHIP COUNTS BY TYPE ===")
        for rel, cnt in sess.execute_read(count_relations_by_type):
            print(f"{rel}: {cnt}")
        print("\n=== RELAÇÕES ENTRE PERSONAGENS ===")
        for frm, rel, to in sess.execute_read(list_character_relations):
            print(f"{frm} -[{rel}]- {to}")
        print("\n=== AMOSTRA (até 200) DE RELAÇÕES GERAIS ===")
        for lN, idN, rel, lM, idM in sess.execute_read(list_all_relations_sample):
            print(f"{lN}({idN}) -[{rel}]- {lM}({idM})")

    driver.close()

if __name__ == "__main__":
    main()
