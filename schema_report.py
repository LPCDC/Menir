#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de relatório de schema/grafo — lista todas labels e tipos de relationships presentes no grafo.
"""

import os
from neo4j import GraphDatabase, basic_auth

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "menir123")
NEO4J_DB   = os.getenv("NEO4J_DB", None)

driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))

def get_session():
    return driver.session(database=NEO4J_DB) if NEO4J_DB else driver.session()

def list_labels(tx):
    q = """
    MATCH (n)
    UNWIND labels(n) AS lbl
    RETURN lbl AS label, count(*) AS count
    ORDER BY count DESC
    """
    return [(rec["label"], rec["count"]) for rec in tx.run(q)]

def list_rel_types(tx):
    q = """
    MATCH ()-[r]->()
    RETURN type(r) AS relType, count(r) AS count
    ORDER BY count DESC
    """
    return [(rec["relType"], rec["count"]) for rec in tx.run(q)]

def main():
    with get_session() as s:
        print("=== Labels no grafo ===")
        for lbl, cnt in s.execute_read(list_labels):
            print(f"{lbl:20} : {cnt}")
        print("\n=== Tipos de relações ===")
        for rel, cnt in s.execute_read(list_rel_types):
            print(f"{rel:20} : {cnt}")
    driver.close()

if __name__ == "__main__":
    main()
