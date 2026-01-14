#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit + Integrity Checker + Export CSV para grafo Livro Débora (Menir).

Gera:
 - Contagem de nós por label
 - Contagem de relações por tipo
 - Personagens órfãos (sem cenas)
 - Cenas sem eventos
 - Relações diretas Character ↔ Character
 - Co-aparecimentos (personagens que compartilham cenas)
 - Exporta seis CSVs:
     * nodes_count.csv (label, count)
     * rels_count.csv (relType, count)
     * orphan_characters.csv (name)
     * scenes_without_events.csv (sceneId, title)
     * char_relations.csv (from, relation, to)
     * coappearances.csv (char1, char2, sharedScenes, sceneIds)
"""

import os
import csv
from neo4j import GraphDatabase, basic_auth

# --- Configuração via env vars ---
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "menir123")
NEO4J_DB   = os.getenv("NEO4J_DB", None)  # opcional: nome do database

driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))

LABELS = ["Work","Chapter","ChapterVersion","Scene","Event","Character","Place","Object","Chunk","EmotionState","SummaryNode"]

def get_session():
    return driver.session(database=NEO4J_DB) if NEO4J_DB else driver.session()

def count_nodes(tx):
    result = []
    for lbl in LABELS:
        cnt = tx.run(f"MATCH (n:{lbl}) RETURN count(n) AS c").single().get("c", 0)
        result.append((lbl, cnt))
    return result

def count_relationships(tx):
    q = "MATCH ()-[r]->() RETURN type(r) AS relType, count(r) AS cnt ORDER BY cnt DESC"
    return [(rec["relType"], rec["cnt"]) for rec in tx.run(q)]

def orphan_characters(tx):
    q = """
    MATCH (c:Character)
    WHERE NOT (c)-[:APPEARS_IN]->(:Scene)
    RETURN c.name AS name
    """
    return [rec["name"] for rec in tx.run(q)]

def scenes_without_events(tx):
    q = """
    MATCH (s:Scene)
    WHERE NOT (s)<-[:OCCURS_IN]-(:Event)
    RETURN s.id AS sceneId, s.title AS title
    """
    return [(rec["sceneId"], rec.get("title")) for rec in tx.run(q)]

def character_relations(tx):
    q = """
    MATCH (c1:Character)-[r]-(c2:Character)
    RETURN distinct c1.name AS from, type(r) AS relation, c2.name AS to
    ORDER BY from, to
    """
    return [(rec["from"], rec["relation"], rec["to"]) for rec in tx.run(q)]

def coappearances(tx):
    q = """
    MATCH (p1:Character)-[:APPEARS_IN]->(s:Scene)<-[:APPEARS_IN]-(p2:Character)
    WHERE p1.id < p2.id
    RETURN p1.name AS char1, p2.name AS char2, count(s) AS sharedCount, collect(s.id) AS sceneIds
    ORDER BY sharedCount DESC
    """
    return [(rec["char1"], rec["char2"], rec["sharedCount"], str(rec["sceneIds"])) for rec in tx.run(q)]

def write_csv(filename, header, rows):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"[CSV] Written: {filename}")

def main():
    with get_session() as sess:
        # Nodes count
        nodes = sess.execute_read(count_nodes)
        write_csv("nodes_count.csv", ["label","count"], nodes)

        # Relationships count
        rels = sess.execute_read(count_relationships)
        write_csv("rels_count.csv", ["relType","count"], rels)

        # Orphan characters
        orphans = sess.execute_read(orphan_characters)
        write_csv("orphan_characters.csv", ["name"], [(o,) for o in orphans])

        # Scenes without events
        sw_noev = sess.execute_read(scenes_without_events)
        write_csv("scenes_without_events.csv", ["sceneId","title"], sw_noev)

        # Character relations
        cr = sess.execute_read(character_relations)
        write_csv("char_relations.csv", ["from","relation","to"], cr)

        # Co-appearances
        cop = sess.execute_read(coappearances)
        write_csv("coappearances.csv", ["char1","char2","sharedCount","sceneIds"], cop)

    driver.close()
    print("[DONE] Auditoria concluída — 6 CSVs gerados no diretório atual.")

if __name__ == "__main__":
    main()
