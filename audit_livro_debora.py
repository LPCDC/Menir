#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit + Integrity Checker para grafo Livro Débora (Menir).

Relatórios:
- contagem de nós por label (labels conhecidas do schema)
- contagem de relações por tipo
- personagens sem cenas associadas
- cenas sem eventos associados
- relações Character ↔ Character (diretas)
- co-aparecimento em cenas (personagens que dividem cenas)
- resumo geral + impressão limpa no console
"""

import os
from neo4j import GraphDatabase, basic_auth

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "menir123")
NEO4J_DB = os.getenv("NEO4J_DB", None)

auth = basic_auth(NEO4J_USER, NEO4J_PASSWORD)
driver = GraphDatabase.driver(NEO4J_URI, auth=auth)

LABELS_TO_CHECK = ["Work","Chapter","ChapterVersion","Scene","Event","Character","Place","Object","Chunk","EmotionState","SummaryNode"]

def get_session():
    return driver.session(database=NEO4J_DB) if NEO4J_DB else driver.session()

def count_nodes(tx):
    res = []
    for lbl in LABELS_TO_CHECK:
        c = tx.run(f"MATCH (n:{lbl}) RETURN count(n) AS c").single().get("c", 0)
        res.append((lbl, c))
    return res

def count_rels(tx):
    q = "MATCH ()-[r]->() RETURN type(r) AS relType, count(r) AS cnt ORDER BY cnt DESC"
    return [(rec["relType"], rec["cnt"]) for rec in tx.run(q)]

def find_orphan_characters(tx):
    q = """
    MATCH (c:Character)
    WHERE NOT (c)-[:APPEARS_IN]->(:Scene)
    RETURN c.name AS orphan
    """
    return [rec["orphan"] for rec in tx.run(q)]

def find_scenes_without_events(tx):
    q = """
    MATCH (s:Scene)
    WHERE NOT (s)<-[:OCCURS_IN]-(:Event)
    RETURN s.id AS sceneId, s.title AS title
    """
    return [(rec["sceneId"], rec.get("title")) for rec in tx.run(q)]

def list_character_relations(tx):
    q = """
    MATCH (c1:Character)-[r]-(c2:Character)
    RETURN distinct c1.name AS from, type(r) AS relation, c2.name AS to
    ORDER BY from, to
    """
    return [(rec["from"], rec["relation"], rec["to"]) for rec in tx.run(q)]

def list_coappearance(tx):
    q = """
    MATCH (p1:Character)-[:APPEARS_IN]->(s:Scene)<-[:APPEARS_IN]-(p2:Character)
    WHERE p1.id < p2.id
    RETURN p1.name AS char1, p2.name AS char2, count(s) AS sharedCount, collect(s.id) AS scenes
    ORDER BY sharedCount DESC
    """
    return [(rec["char1"], rec["char2"], rec["sharedCount"], rec["scenes"]) for rec in tx.run(q)]

def main():
    with get_session() as sess:
        print("=== NODE COUNTS ===")
        for lbl, cnt in sess.execute_read(count_nodes):
            print(f"{lbl:15} : {cnt}")

        print("\n=== RELATIONSHIP COUNTS ===")
        for rel, cnt in sess.execute_read(count_rels):
            print(f"{rel:20} : {cnt}")

        print("\n=== ORPHAN CHARACTERS (sem cenas) ===")
        orphans = sess.execute_read(find_orphan_characters)
        if orphans:
            for o in orphans:
                print(" -", o)
        else:
            print("Nenhum personagem órfão encontrado.")

        print("\n=== SCENES WITHOUT EVENTS ===")
        noev = sess.execute_read(find_scenes_without_events)
        if noev:
            for sid, title in noev:
                print(" -", sid, "|", title)
        else:
            print("Todas as cenas têm pelo menos um evento.")

        print("\n=== CHARACTER ↔ CHARACTER DIRECT RELATIONS ===")
        charrels = sess.execute_read(list_character_relations)
        if charrels:
            for frm, rel, to in charrels:
                print(f"{frm} -[{rel}]-> {to}")
        else:
            print("Nenhuma relação direta entre personagens encontrada.")

        print("\n=== CO-APPEARANCE (characters compartilham cenas) ===")
        for c1, c2, cnt, scenes in sess.execute_read(list_coappearance):
            print(f"{c1} ⇄ {c2} — cenas compartilhadas: {cnt} — {scenes}")

    driver.close()

if __name__ == "__main__":
    main()
