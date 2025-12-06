#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full-reset + ingestão + auditoria para Livro Débora (Menir).

Passos:
1. Deleta todos os nós e relações existentes
2. Recria schema v2 (constraints + índices)
3. Cria Work / Chapter / ChapterVersion
4. Ingesta Cap. 1 via JSON embutido
5. Executa auditoria: conta nós/rel, detecta órfãos, cenas sem eventos, relações, co-aparecimentos
6. Exporta relatórios CSV
"""

import os
import json
import hashlib
import csv
from neo4j import GraphDatabase, basic_auth

### — Configurações de acesso — ###
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "menir123")
NEO4J_DB   = os.getenv("NEO4J_DB", None)

# Metadados da obra
WORK_ID = "better_in_manhattan"
WORK_TITLE = "Better in Manhattan"
WORK_AUTHOR = "Débora Vezzali"
CHAPTER_ID = "cap1_better"
CHAPTER_NUMBER = 1
CHAPTER_TITLE = "Capítulo 1"
CHAPTER_VERSION_ID = "cap1_better_v1.0"
CHAPTER_VERSION_TAG = "v1.0"
CHAPTER_SOURCE_TYPE = "json"

def detect_db_origin(uri: str) -> str:
    """Detecta origem do banco para rastreabilidade."""
    lower = uri.lower()
    if lower.startswith("bolt://localhost") or lower.startswith("bolt://127.0.0.1"):
        return "local"
    if lower.startswith("neo4j+s://") or "databases.neo4j.io" in lower:
        return "aura"
    return "unknown"

DB_ORIGIN = detect_db_origin(NEO4J_URI)

# JSON embutido completo do Cap. 1
BUILTIN_CAP1 = {
    "scenes": [
        {
            "sceneId": "scene_01",
            "sceneIndex": 1,
            "title": "Manhã na casa dos Howell",
            "relativeTime": "manhã",
            "place": {"placeId":"place_Howell_Apartment","name":"Apartamento Howell","type":"apartment"},
            "characters":[
                {"id":"char_Caroline","name":"Caroline Howell","role":"protagonist"},
                {"id":"char_Olivia","name":"Olivia Howell","role":"family"},
                {"id":"char_Andy","name":"Andy Howell","role":"family"}
            ],
            "events":[
                {"eventId":"event_01_01","eventIndex":1,"summary":"Caroline acorda com 'Here Comes the Sun'","eventType":"ACTION"},
                {"eventId":"event_01_02","eventIndex":2,"summary":"Caroline toma café com Olivia","eventType":"ACTION"},
                {"eventId":"event_01_03","eventIndex":3,"summary":"Caroline recebe bilhete do pai","eventType":"REVELATION"},
                {"eventId":"event_01_04","eventIndex":4,"summary":"Caroline encontra Andy e vai para escola","eventType":"ACTION"}
            ],
            "objects":[]
        },
        {
            "sceneId": "scene_02",
            "sceneIndex": 2,
            "title": "Chegada à Trailblazer Academy",
            "relativeTime":"início do dia",
            "place": {"placeId":"place_Trailblazer_Academy","name":"Trailblazer Academy","type":"school"},
            "characters":[
                {"id":"char_Caroline","name":"Caroline Howell","role":"protagonist"},
                {"id":"char_Lauren","name":"Lauren","role":"friend"},
                {"id":"char_DirectorSmith","name":"Diretor Smith","role":"staff"}
            ],
            "events":[
                {"eventId":"event_02_01","eventIndex":1,"summary":"Reencontro com Lauren","eventType":"ACTION"},
                {"eventId":"event_02_02","eventIndex":2,"summary":"Sessão de boas-vindas no auditório","eventType":"ACTION"},
                {"eventId":"event_02_03","eventIndex":3,"summary":"Observação da ausência de Spencer","eventType":"OBSERVATION"}
            ],
            "objects":[]
        },
        {
            "sceneId": "scene_03",
            "sceneIndex": 3,
            "title": "Aula de Educação Física",
            "relativeTime": "manhã",
            "place": {"placeId":"place_Gym_Trailblazer","name":"Ginásio da escola","type":"school_gym"},
            "characters":[
                {"id":"char_Caroline","name":"Caroline Howell","role":"protagonist"},
                {"id":"char_DeanBellini","name":"Dean Bellini","role":"student"},
                {"id":"char_Teacher_ODonnel","name":"Sr. O'Donnel","role":"staff"}
            ],
            "events":[
                {"eventId":"event_03_01","eventIndex":1,"summary":"Dean chega atrasado e senta ao lado de Caroline","eventType":"ACTION"},
                {"eventId":"event_03_02","eventIndex":2,"summary":"Dean convida Caroline para almoçar; ela recusa","eventType":"DIALOGUE"}
            ],
            "objects":[]
        },
        {
            "sceneId": "scene_04",
            "sceneIndex": 4,
            "title": "Almoço no refeitório da escola",
            "relativeTime": "meio-dia",
            "place": {"placeId":"place_School_Cafeteria","name":"Refeitório da escola","type":"school_cafeteria"},
            "characters":[
                {"id":"char_Caroline","name":"Caroline Howell","role":"protagonist"},
                {"id":"char_Lauren","name":"Lauren","role":"friend"},
                {"id":"char_Matt","name":"Matt","role":"student"},
                {"id":"char_DeanBellini","name":"Dean Bellini","role":"student"}
            ],
            "events":[
                {"eventId":"event_04_01","eventIndex":1,"summary":"Dean convida o grupo para festa na sexta-feira","eventType":"INVITATION"},
                {"eventId":"event_04_02","eventIndex":2,"summary":"Flashback: primeiro beijo de Caroline com Spencer em festa na casa do Dean","eventType":"MEMORY"},
                {"eventId":"event_04_03","eventIndex":3,"summary":"Dean revela que Lauren e Matt estão namorando; Caroline fica em choque","eventType":"REVELATION"},
                {"eventId":"event_04_04","eventIndex":4,"summary":"Caroline sai do refeitório abalada","eventType":"ACTION"}
            ],
            "objects":[]
        }
    ],
    "characters":[
        {"id":"char_Caroline","name":"Caroline Howell","role":"protagonist"},
        {"id":"char_Spencer","name":"Spencer","role":"friend"},
        {"id":"char_Lauren","name":"Lauren","role":"friend"},
        {"id":"char_Matt","name":"Matt","role":"student"},
        {"id":"char_DeanBellini","name":"Dean Bellini","role":"student"},
        {"id":"char_Andy","name":"Andy Howell","role":"family"},
        {"id":"char_Olivia","name":"Olivia Howell","role":"family"},
        {"id":"char_DirectorSmith","name":"Diretor Smith","role":"staff"},
        {"id":"char_Teacher_ODonnel","name":"Sr. O'Donnel","role":"staff"}
    ],
    "places":[
        {"placeId":"place_Howell_Apartment","name":"Apartamento Howell","type":"apartment"},
        {"placeId":"place_Trailblazer_Academy","name":"Trailblazer Academy","type":"school"},
        {"placeId":"place_Gym_Trailblazer","name":"Ginásio da escola","type":"school_gym"},
        {"placeId":"place_School_Cafeteria","name":"Refeitório da escola","type":"school_cafeteria"}
    ],
    "objects":[]
}

# Schema statements
SCHEMA_STMTS = [
    "CREATE CONSTRAINT work_id_unique IF NOT EXISTS FOR (w:Work) REQUIRE w.id IS UNIQUE",
    "CREATE CONSTRAINT chapter_id_unique IF NOT EXISTS FOR (c:Chapter) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT chapterVersion_id_unique IF NOT EXISTS FOR (v:ChapterVersion) REQUIRE v.id IS UNIQUE",
    "CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS FOR (k:Chunk) REQUIRE k.id IS UNIQUE",
    "CREATE CONSTRAINT scene_id_unique IF NOT EXISTS FOR (s:Scene) REQUIRE s.id IS UNIQUE",
    "CREATE CONSTRAINT event_id_unique IF NOT EXISTS FOR (e:Event) REQUIRE e.id IS UNIQUE",
    "CREATE CONSTRAINT character_id_unique IF NOT EXISTS FOR (c:Character) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT place_id_unique IF NOT EXISTS FOR (p:Place) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT object_id_unique IF NOT EXISTS FOR (o:Object) REQUIRE o.id IS UNIQUE",
    "CREATE CONSTRAINT emotionState_id_unique IF NOT EXISTS FOR (em:EmotionState) REQUIRE em.id IS UNIQUE",
    "CREATE CONSTRAINT summaryNode_id_unique IF NOT EXISTS FOR (sn:SummaryNode) REQUIRE sn.id IS UNIQUE",
    "CREATE INDEX character_name_idx IF NOT EXISTS FOR (c:Character) ON (c.name)",
    "CREATE INDEX scene_index_idx IF NOT EXISTS FOR (s:Scene) ON (s.sceneIndex)",
    "CREATE INDEX event_index_idx IF NOT EXISTS FOR (e:Event) ON (e.eventIndex)"
]

LABELS = ["Work","Chapter","ChapterVersion","Scene","Event","Character","Place","Object","Chunk","EmotionState","SummaryNode"]

driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))

def get_session():
    return driver.session(database=NEO4J_DB) if NEO4J_DB else driver.session()

def clear_graph(tx):
    tx.run("MATCH (n) DETACH DELETE n")

def init_schema(tx):
    for stmt in SCHEMA_STMTS:
        tx.run(stmt)

def create_work(tx):
    tx.run("""
        MERGE (w:Work {id: $id})
        SET w.title = $title,
            w.authorAlias = $authorAlias,
            w.status = $status,
            w.databaseOrigin = $dbOrigin,
            w.createdAt = coalesce(w.createdAt, datetime()),
            w.updatedAt = datetime()
        """,
        id=WORK_ID, title=WORK_TITLE, authorAlias=WORK_AUTHOR, status="in_progress", dbOrigin=DB_ORIGIN
    )

def create_chapter(tx):
    tx.run("""
        MERGE (c:Chapter {id: $id})
        SET c.number = $number,
            c.title = $title,
            c.shortSlug = $shortSlug,
            c.databaseOrigin = $dbOrigin,
            c.updatedAt = datetime()
        MERGE (w:Work {id: $workId})
        MERGE (w)-[:HAS_CHAPTER]->(c)
        """,
        id=CHAPTER_ID, number=CHAPTER_NUMBER, title=CHAPTER_TITLE, shortSlug="cap1_better", workId=WORK_ID, dbOrigin=DB_ORIGIN
    )

def create_chapter_version(tx):
    tx.run("""
        MATCH (c:Chapter {id: $chapterId})
        MERGE (v:ChapterVersion {id: $id})
        SET v.versionTag = $versionTag,
            v.sourceType = $sourceType,
            v.isCanonical = true,
            v.databaseOrigin = $dbOrigin,
            v.createdAt = coalesce(v.createdAt, datetime()),
            v.updatedAt = datetime()
        MERGE (v)-[:VERSION_OF]->(c)
        """,
        chapterId=CHAPTER_ID, id=CHAPTER_VERSION_ID, versionTag=CHAPTER_VERSION_TAG, sourceType=CHAPTER_SOURCE_TYPE, dbOrigin=DB_ORIGIN
    )

def merge_character(tx, ch):
    tx.run("""
        MERGE (c:Character {id: $id})
        SET c.name = $name, c.role = $role, c.updatedAt = datetime()
        """,
        id=ch["id"], name=ch.get("name"), role=ch.get("role", "unknown")
    )

def merge_place(tx, pl):
    tx.run("""
        MERGE (p:Place {id: $id})
        SET p.name = $name, p.type = $type, p.updatedAt = datetime()
        """,
        id=pl["placeId"], name=pl.get("name"), type=pl.get("type", "unknown")
    )

def merge_scene_and_links(tx, scene, previous_scene_id):
    # Scene
    tx.run("""
        MATCH (v:ChapterVersion {id: $chapterVersionId})
        MERGE (s:Scene {id: $sceneId})
        SET s.sceneIndex = $sceneIndex, s.title = $title, s.relativeTime = $relativeTime, s.updatedAt = datetime()
        MERGE (v)-[:HAS_SCENE]->(s)
        """,
        chapterVersionId=CHAPTER_VERSION_ID, sceneId=scene["sceneId"], sceneIndex=scene.get("sceneIndex", 0),
        title=scene.get("title"), relativeTime=scene.get("relativeTime")
    )
    
    # NEXT_SCENE
    if previous_scene_id:
        tx.run("""
            MATCH (prev:Scene {id: $prevId})
            MATCH (curr:Scene {id: $currId})
            MERGE (prev)-[:NEXT_SCENE]->(curr)
            """,
            prevId=previous_scene_id, currId=scene["sceneId"]
        )
    
    # Place
    place = scene.get("place")
    if place:
        tx.run("""
            MERGE (p:Place {id: $placeId})
            SET p.name = $placeName, p.type = $placeType, p.updatedAt = datetime()
            MATCH (s:Scene {id: $sceneId})
            MERGE (s)-[:SET_IN]->(p)
            """,
            placeId=place["placeId"], placeName=place.get("name"), placeType=place.get("type", "unknown"), sceneId=scene["sceneId"]
        )
    
    # Characters
    for ch in scene.get("characters", []):
        tx.run("""
            MERGE (c:Character {id: $charId})
            SET c.name = $charName, c.role = $charRole, c.updatedAt = datetime()
            MATCH (s:Scene {id: $sceneId})
            MERGE (c)-[:APPEARS_IN]->(s)
            """,
            charId=ch["id"], charName=ch.get("name"), charRole=ch.get("role", "unknown"), sceneId=scene["sceneId"]
        )
    
    # Events + NEXT_EVENT
    events = sorted(scene.get("events", []), key=lambda e: e.get("eventIndex", 0))
    prev_event_id = None
    for ev in events:
        tx.run("""
            MATCH (s:Scene {id: $sceneId})
            MERGE (e:Event {id: $eventId})
            SET e.eventIndex = $eventIndex, e.summary = $summary, e.eventType = $eventType, e.updatedAt = datetime()
            MERGE (e)-[:OCCURS_IN]->(s)
            """,
            sceneId=scene["sceneId"], eventId=ev["eventId"], eventIndex=ev.get("eventIndex", 0),
            summary=ev.get("summary"), eventType=ev.get("eventType", "ACTION")
        )
        if prev_event_id:
            tx.run("""
                MATCH (e1:Event {id: $prevId})
                MATCH (e2:Event {id: $currId})
                MERGE (e1)-[:NEXT_EVENT]->(e2)
                """,
                prevId=prev_event_id, currId=ev["eventId"]
            )
        prev_event_id = ev["eventId"]

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
    q = "MATCH (c:Character) WHERE NOT (c)-[:APPEARS_IN]->(:Scene) RETURN c.name AS name"
    return [rec["name"] for rec in tx.run(q)]

def scenes_without_events(tx):
    q = "MATCH (s:Scene) WHERE NOT (s)<-[:OCCURS_IN]-(:Event) RETURN s.id AS sceneId, s.title AS title"
    return [(rec["sceneId"], rec.get("title")) for rec in tx.run(q)]

def character_relations(tx):
    q = "MATCH (c1:Character)-[r]-(c2:Character) RETURN distinct c1.name AS from, type(r) AS relation, c2.name AS to ORDER BY from, to"
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
    print(f"[CSV] {filename}")

def main():
    print(f"[INFO] Conectando ao Neo4j ({DB_ORIGIN}) em {NEO4J_URI}")
    
    with get_session() as sess:
        # 1) Limpa tudo
        print("[1/6] Limpando grafo...")
        sess.execute_write(clear_graph)
        print("  ✓ Grafo limpo.")
        
        # 2) Recria schema
        print("[2/6] Recriando schema v2...")
        sess.execute_write(init_schema)
        print("  ✓ Schema recriado (11 constraints + 3 indexes).")
        
        # 3) Cria estrutura básica
        print("[3/6] Criando Work/Chapter/ChapterVersion...")
        sess.execute_write(create_work)
        sess.execute_write(create_chapter)
        sess.execute_write(create_chapter_version)
        print(f"  ✓ Estrutura base criada (databaseOrigin={DB_ORIGIN}).")
        
        # 4) Ingesta Cap. 1
        print("[4/6] Ingerindo Cap. 1 (4 cenas, 13 eventos, 9 personagens)...")
        for ch in BUILTIN_CAP1.get("characters", []):
            sess.execute_write(merge_character, ch)
        for pl in BUILTIN_CAP1.get("places", []):
            sess.execute_write(merge_place, pl)
        scenes = sorted(BUILTIN_CAP1.get("scenes", []), key=lambda s: s.get("sceneIndex", 0))
        previous_scene_id = None
        for scene in scenes:
            sess.execute_write(merge_scene_and_links, scene, previous_scene_id)
            previous_scene_id = scene["sceneId"]
        print("  ✓ Dados do Cap. 1 ingeridos.")
        
        # 5) Auditoria
        print("[5/6] Executando auditoria...")
        nodes = sess.execute_read(count_nodes)
        write_csv("rebuild_nodes_count.csv", ["label","count"], nodes)
        
        rels = sess.execute_read(count_relationships)
        write_csv("rebuild_rels_count.csv", ["relType","count"], rels)
        
        orphans = sess.execute_read(orphan_characters)
        write_csv("rebuild_orphan_characters.csv", ["name"], [(o,) for o in orphans])
        
        sw_noev = sess.execute_read(scenes_without_events)
        write_csv("rebuild_scenes_without_events.csv", ["sceneId","title"], sw_noev)
        
        cr = sess.execute_read(character_relations)
        write_csv("rebuild_char_relations.csv", ["from","relation","to"], cr)
        
        cop = sess.execute_read(coappearances)
        write_csv("rebuild_coappearances.csv", ["char1","char2","sharedCount","sceneIds"], cop)
        
        print("  ✓ Auditoria concluída; 6 CSVs gerados.")
        
        # 6) Resumo
        print("[6/6] Resumo:")
        total_nodes = sum(cnt for _, cnt in nodes)
        total_rels = sum(cnt for _, cnt in rels)
        print(f"  • Total de nós: {total_nodes}")
        print(f"  • Total de relações: {total_rels}")
        print(f"  • Personagens órfãos: {len(orphans)}")
        print(f"  • Cenas sem eventos: {len(sw_noev)}")

    driver.close()
    print("\n[DONE] Rebuild + Ingest + Audit concluído com sucesso!")
    print("Próximo passo: abra o Neo4j Browser e execute as queries de audit_queries.cypher")

if __name__ == "__main__":
    main()
