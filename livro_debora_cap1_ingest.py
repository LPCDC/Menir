#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
All-in-one para Codespace – Livro Débora (Better in Manhattan) – Cap. 1

Funcionalidades:
- Conexão com Neo4j (Aura ou Desktop) via variáveis de ambiente.
- (Opcional) Criação do schema v2 (constraints + índices).
- Ingestão de:
    - Work, Chapter, ChapterVersion (se quiser reforçar), e
    - Scene, Event, Character, Place,
  a partir de JSON externo ou JSON embutido.

Uso típico:
    export NEO4J_URI=...
    export NEO4J_USER=...
    export NEO4J_PASSWORD=...
    export NEO4J_DB=neo4j   # se necessário

    python livro_debora_cap1_ingest.py --init-schema
    python livro_debora_cap1_ingest.py --ingest-builtin
    # ou:
    python livro_debora_cap1_ingest.py --ingest-json cap1_structure.json
"""

import os
import json
import hashlib
import argparse
from neo4j import GraphDatabase, basic_auth

# ============================================================
# CONFIG – CREDENCIAIS VIA ENV VARS
# ============================================================

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j")
NEO4J_DB = os.getenv("NEO4J_DB", None)  # se usar DB com nome específico


def detect_db_origin(uri: str) -> str:
    """Detecta origem do banco para rastreabilidade (local vs Aura/remote)."""
    lower = uri.lower()
    if lower.startswith("bolt://localhost") or lower.startswith("bolt://127.0.0.1"):
        return "local"
    if lower.startswith("neo4j+s://") or "databases.neo4j.io" in lower:
        return "aura"
    return "unknown"


DB_ORIGIN = detect_db_origin(NEO4J_URI)

WORK_ID = "better_in_manhattan"
WORK_TITLE = "Better in Manhattan"
WORK_AUTHOR_ALIAS = "Débora Vezzali"

CHAPTER_ID = "cap1_better"
CHAPTER_NUMBER = 1
CHAPTER_TITLE = "Capítulo 1"

# IMPORTANTE: ajuste se o id da ChapterVersion for outro
CHAPTER_VERSION_ID = "cap1_better_v1.0"
CHAPTER_VERSION_TAG = "v1.0"
CHAPTER_SOURCE_TYPE = "pdf"  # ou "file"/"md" etc.

# ============================================================
# JSON EMBUTIDO – TEMPLATE INICIAL DO CAPÍTULO 1
# (edite à vontade aqui dentro)
# ============================================================

BUILTIN_CAP1_JSON = {
    "workId": WORK_ID,
    "chapterId": CHAPTER_ID,
    "chapterVersionId": CHAPTER_VERSION_ID,
    "scenes": [
        {
            "sceneId": "scene_01",
            "sceneIndex": 1,
            "title": "Manhã na casa dos Howell",
            "relativeTime": "manhã",
            "place": {
                "placeId": "place_Howell_Apartment",
                "name": "Apartamento Howell",
                "type": "apartment"
            },
            "characters": [
                {"id": "char_Caroline", "name": "Caroline Howell", "role": "protagonist"},
                {"id": "char_Olivia", "name": "Olivia Howell", "role": "family"},
                {"id": "char_Andy", "name": "Andy Howell", "role": "family"}
            ],
            "events": [
                {
                    "eventId": "event_01_01",
                    "eventIndex": 1,
                    "summary": "Caroline acorda com 'Here Comes the Sun'",
                    "eventType": "ACTION"
                },
                {
                    "eventId": "event_01_02",
                    "eventIndex": 2,
                    "summary": "Caroline toma café com Olivia",
                    "eventType": "ACTION"
                },
                {
                    "eventId": "event_01_03",
                    "eventIndex": 3,
                    "summary": "Caroline recebe bilhete do pai",
                    "eventType": "REVELATION"
                },
                {
                    "eventId": "event_01_04",
                    "eventIndex": 4,
                    "summary": "Caroline encontra Andy e vai para escola",
                    "eventType": "ACTION"
                }
            ],
            "objects": []
        },
        {
            "sceneId": "scene_02",
            "sceneIndex": 2,
            "title": "Chegada à Trailblazer Academy",
            "relativeTime": "início do dia",
            "place": {
                "placeId": "place_Trailblazer_Academy",
                "name": "Trailblazer Academy",
                "type": "school"
            },
            "characters": [
                {"id": "char_Caroline", "name": "Caroline Howell", "role": "protagonist"},
                {"id": "char_Lauren", "name": "Lauren", "role": "friend"},
                {"id": "char_DirectorSmith", "name": "Diretor Smith", "role": "staff"}
            ],
            "events": [
                {
                    "eventId": "event_02_01",
                    "eventIndex": 1,
                    "summary": "Reencontro com Lauren no colégio",
                    "eventType": "ACTION"
                },
                {
                    "eventId": "event_02_02",
                    "eventIndex": 2,
                    "summary": "Sessão de boas-vindas no auditório",
                    "eventType": "ACTION"
                },
                {
                    "eventId": "event_02_03",
                    "eventIndex": 3,
                    "summary": "Observação da ausência de Spencer",
                    "eventType": "OBSERVATION"
                }
            ],
            "objects": []
        },
        {
            "sceneId": "scene_03",
            "sceneIndex": 3,
            "title": "Aula de Educação Física",
            "relativeTime": "manhã",
            "place": {
                "placeId": "place_Gym_Trailblazer",
                "name": "Ginásio da escola",
                "type": "school_gym"
            },
            "characters": [
                {"id": "char_Caroline", "name": "Caroline Howell", "role": "protagonist"},
                {"id": "char_DeanBellini", "name": "Dean Bellini", "role": "student"},
                {"id": "char_Teacher_ODonnel", "name": "Sr. O'Donnel", "role": "staff"}
            ],
            "events": [
                {
                    "eventId": "event_03_01",
                    "eventIndex": 1,
                    "summary": "Dean chega atrasado e senta ao lado de Caroline",
                    "eventType": "ACTION"
                },
                {
                    "eventId": "event_03_02",
                    "eventIndex": 2,
                    "summary": "Dean convida Caroline para almoçar; ela recusa",
                    "eventType": "DIALOGUE"
                }
            ],
            "objects": []
        },
        {
            "sceneId": "scene_04",
            "sceneIndex": 4,
            "title": "Almoço no refeitório da escola",
            "relativeTime": "meio-dia",
            "place": {
                "placeId": "place_School_Cafeteria",
                "name": "Refeitório da escola",
                "type": "school_cafeteria"
            },
            "characters": [
                {"id": "char_Caroline", "name": "Caroline Howell", "role": "protagonist"},
                {"id": "char_Lauren", "name": "Lauren", "role": "friend"},
                {"id": "char_Matt", "name": "Matt", "role": "student"},
                {"id": "char_DeanBellini", "name": "Dean Bellini", "role": "student"}
            ],
            "events": [
                {
                    "eventId": "event_04_01",
                    "eventIndex": 1,
                    "summary": "Dean convida o grupo para festa na sexta-feira",
                    "eventType": "INVITATION"
                },
                {
                    "eventId": "event_04_02",
                    "eventIndex": 2,
                    "summary": "Flashback: primeiro beijo de Caroline com Spencer em festa na casa do Dean",
                    "eventType": "MEMORY"
                },
                {
                    "eventId": "event_04_03",
                    "eventIndex": 3,
                    "summary": "Dean revela que Lauren e Matt estão namorando; Caroline fica em choque",
                    "eventType": "REVELATION"
                },
                {
                    "eventId": "event_04_04",
                    "eventIndex": 4,
                    "summary": "Caroline sai do refeitório abalada",
                    "eventType": "ACTION"
                }
            ],
            "objects": []
        }
        # Aqui você pode continuar as cenas 5..10 etc.
    ],
    "characters": [
        {"id": "char_Caroline", "name": "Caroline Howell", "role": "protagonist"},
        {"id": "char_Spencer", "name": "Spencer", "role": "friend"},
        {"id": "char_Lauren", "name": "Lauren", "role": "friend"},
        {"id": "char_Matt", "name": "Matt", "role": "student"},
        {"id": "char_DeanBellini", "name": "Dean Bellini", "role": "student"},
        {"id": "char_Andy", "name": "Andy Howell", "role": "family"},
        {"id": "char_Olivia", "name": "Olivia Howell", "role": "family"},
        {"id": "char_DirectorSmith", "name": "Diretor Smith", "role": "staff"},
        {"id": "char_Teacher_ODonnel", "name": "Sr. O'Donnel", "role": "staff"}
    ],
    "places": [
        {"placeId": "place_Howell_Apartment", "name": "Apartamento Howell", "type": "apartment"},
        {"placeId": "place_Trailblazer_Academy", "name": "Trailblazer Academy", "type": "school"},
        {"placeId": "place_Gym_Trailblazer", "name": "Ginásio da escola", "type": "school_gym"},
        {"placeId": "place_School_Cafeteria", "name": "Refeitório da escola", "type": "school_cafeteria"}
    ],
    "objects": []
}

# ============================================================
# CONEXÃO NEO4J
# ============================================================

auth = basic_auth(NEO4J_USER, NEO4J_PASSWORD)
driver = GraphDatabase.driver(NEO4J_URI, auth=auth)

def get_session():
    if NEO4J_DB:
        return driver.session(database=NEO4J_DB)
    return driver.session()

# ============================================================
# SCHEMA (se quiser rodar daqui também)
# ============================================================

SCHEMA_STATEMENTS = [
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

def init_schema():
    with get_session() as sess:
        for stmt in SCHEMA_STATEMENTS:
            try:
                sess.run(stmt)
            except Exception as e:
                print(f"[WARN] Erro ao aplicar: {stmt}\n  → {e}")
    print("[OK] Schema v2 garantido (constraints + índices).")

# ============================================================
# HELPERS DE NÓS BÁSICOS
# ============================================================

def tx_create_work(tx):
    tx.run(
        """
        MERGE (w:Work {id: $id})
        SET w.title = $title,
            w.authorAlias = $authorAlias,
            w.status = $status,
            w.databaseOrigin = $dbOrigin,
            w.createdAt = coalesce(w.createdAt, datetime()),
            w.updatedAt = datetime()
        """,
        id=WORK_ID,
        title=WORK_TITLE,
        authorAlias=WORK_AUTHOR_ALIAS,
        status="in_progress",
        dbOrigin=DB_ORIGIN
    )

def tx_create_chapter(tx):
    tx.run(
        """
        MERGE (c:Chapter {id: $id})
        SET c.number = $number,
            c.title = $title,
            c.shortSlug = $shortSlug,
            c.databaseOrigin = $dbOrigin,
            c.updatedAt = datetime()
        MERGE (w:Work {id: $workId})
        MERGE (w)-[:HAS_CHAPTER]->(c)
        """,
        id=CHAPTER_ID,
        number=CHAPTER_NUMBER,
        title=CHAPTER_TITLE,
        shortSlug="cap1_better",
        workId=WORK_ID,
        dbOrigin=DB_ORIGIN
    )

def tx_create_chapter_version(tx, hash_value=None):
    tx.run(
        """
        MATCH (c:Chapter {id: $chapterId})
        MERGE (v:ChapterVersion {id: $id})
        SET v.versionTag = $versionTag,
            v.sourceType = $sourceType,
            v.hash = coalesce($hashVal, v.hash),
            v.isCanonical = true,
            v.sourceFilePath = $sourceFilePath,
            v.databaseOrigin = $dbOrigin,
            v.createdAt = coalesce(v.createdAt, datetime()),
            v.updatedAt = datetime()
        MERGE (v)-[:VERSION_OF]->(c)
        """,
        chapterId=CHAPTER_ID,
        id=CHAPTER_VERSION_ID,
        versionTag=CHAPTER_VERSION_TAG,
        sourceType=CHAPTER_SOURCE_TYPE,
        hashVal=hash_value,
        sourceFilePath=None,
        dbOrigin=DB_ORIGIN
    )

def compute_hash_file(path, algo="sha256"):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

# ============================================================
# INGESTÃO DE ENTIDADES (CHAR/PLACE/SCENE/EVENT)
# ============================================================

def ingest_cap1_from_dict(data: dict):
    """
    data: estrutura como BUILTIN_CAP1_JSON ou JSON carregado de arquivo.
    """
    with get_session() as sess:
        # Garantir Work, Chapter, ChapterVersion (sem destruir nada)
        sess.execute_write(tx_create_work)
        sess.execute_write(tx_create_chapter)
        sess.execute_write(tx_create_chapter_version, hash_value=None)

        # Characters
        for ch in data.get("characters", []):
            sess.execute_write(tx_merge_character, ch)

        # Places
        for pl in data.get("places", []):
            sess.execute_write(tx_merge_place, pl)

        # Scenes + Events
        scenes = sorted(data.get("scenes", []), key=lambda s: s.get("sceneIndex", 0))
        previous_scene_id = None
        for scene in scenes:
            sess.execute_write(tx_merge_scene_and_links, scene, previous_scene_id)
            previous_scene_id = scene["sceneId"]

        print("[OK] Ingestão de Cap. 1 concluída.")

def tx_merge_character(tx, ch):
    tx.run(
        """
        MERGE (c:Character {id: $id})
        SET c.name = $name,
            c.role = $role,
            c.updatedAt = datetime()
        """,
        id=ch["id"],
        name=ch.get("name"),
        role=ch.get("role", "unknown")
    )

def tx_merge_place(tx, pl):
    tx.run(
        """
        MERGE (p:Place {id: $id})
        SET p.name = $name,
            p.type = $type,
            p.city = $city,
            p.neighborhood = $neighborhood,
            p.updatedAt = datetime()
        """,
        id=pl["placeId"],
        name=pl.get("name"),
        type=pl.get("type", "unknown"),
        city=pl.get("city"),
        neighborhood=pl.get("neighborhood")
    )

def tx_merge_scene_and_links(tx, scene, previous_scene_id):
    """
    Cria Scene, liga à ChapterVersion, Place, Characters, Events e NEXT_SCENE/NEXT_EVENT.
    """
    # Scene
    tx.run(
        """
        MATCH (v:ChapterVersion {id: $chapterVersionId})
        MERGE (s:Scene {id: $sceneId})
        SET s.sceneIndex = $sceneIndex,
            s.title = $title,
            s.relativeTime = $relativeTime,
            s.updatedAt = datetime()
        MERGE (v)-[:HAS_SCENE]->(s)
        """,
        chapterVersionId=CHAPTER_VERSION_ID,
        sceneId=scene["sceneId"],
        sceneIndex=scene.get("sceneIndex", 0),
        title=scene.get("title"),
        relativeTime=scene.get("relativeTime")
    )

    # NEXT_SCENE
    if previous_scene_id:
        tx.run(
            """
            MATCH (prev:Scene {id: $prevId})
            MATCH (curr:Scene {id: $currId})
            MERGE (prev)-[:NEXT_SCENE]->(curr)
            """,
            prevId=previous_scene_id,
            currId=scene["sceneId"]
        )

    # Place
    place = scene.get("place")
    if place:
        tx.run(
            """
            MERGE (p:Place {id: $placeId})
            SET p.name = $placeName,
                p.type = $placeType,
                p.updatedAt = datetime()
            MATCH (s:Scene {id: $sceneId})
            MERGE (s)-[:SET_IN]->(p)
            """,
            placeId=place["placeId"],
            placeName=place.get("name"),
            placeType=place.get("type", "unknown"),
            sceneId=scene["sceneId"]
        )

    # Characters / APPEARS_IN
    for ch in scene.get("characters", []):
        tx.run(
            """
            MERGE (c:Character {id: $charId})
            SET c.name = $charName,
                c.role = $charRole,
                c.updatedAt = datetime()
            MATCH (s:Scene {id: $sceneId})
            MERGE (c)-[:APPEARS_IN]->(s)
            """,
            charId=ch["id"],
            charName=ch.get("name"),
            charRole=ch.get("role", "unknown"),
            sceneId=scene["sceneId"]
        )

    # Events + NEXT_EVENT
    events = sorted(scene.get("events", []), key=lambda e: e.get("eventIndex", 0))
    prev_event_id = None
    for ev in events:
        tx.run(
            """
            MATCH (s:Scene {id: $sceneId})
            MERGE (e:Event {id: $eventId})
            SET e.eventIndex = $eventIndex,
                e.summary = $summary,
                e.eventType = $eventType,
                e.updatedAt = datetime()
            MERGE (e)-[:OCCURS_IN]->(s)
            """,
            sceneId=scene["sceneId"],
            eventId=ev["eventId"],
            eventIndex=ev.get("eventIndex", 0),
            summary=ev.get("summary"),
            eventType=ev.get("eventType", "ACTION")
        )
        if prev_event_id:
            tx.run(
                """
                MATCH (e1:Event {id: $prevId})
                MATCH (e2:Event {id: $currId})
                MERGE (e1)-[:NEXT_EVENT]->(e2)
                """,
                prevId=prev_event_id,
                currId=ev["eventId"]
            )
        prev_event_id = ev["eventId"]

# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="All-in-one ingest para Livro Débora – Cap. 1")
    parser.add_argument("--init-schema", action="store_true", help="Cria/garante schema v2 (constraints + índices)")
    parser.add_argument("--ensure-core", action="store_true", help="Garante Work, Chapter, ChapterVersion básicos")
    parser.add_argument("--chapter-file", type=str, help="Arquivo de texto/PDF para computar hash (opcional)")
    parser.add_argument("--ingest-builtin", action="store_true", help="Ingere Cap. 1 usando JSON embutido")
    parser.add_argument("--ingest-json", type=str, help="Ingere Cap. 1 a partir de arquivo JSON externo")
    args = parser.parse_args()

    # Teste rápido de conexão
    try:
        driver.verify_connectivity()
        print(f"[OK] Conectado ao Neo4j ({DB_ORIGIN}) em {NEO4J_URI}")
    except Exception as e:
        print(f"[ERRO] Falha ao conectar ao Neo4j: {e}")
        return

    if args.init_schema:
        init_schema()

    # Garante Work/Chapter/ChapterVersion (opcional, mas seguro)
    if args.ensure_core or args.ingest_builtin or args.ingest_json:
        with get_session() as sess:
            sess.execute_write(tx_create_work)
            sess.execute_write(tx_create_chapter)
            hash_val = None
            if args.chapter_file:
                hash_val = compute_hash_file(args.chapter_file)
                print(f"[INFO] Hash do arquivo ({args.chapter_file}): {hash_val}")
            sess.execute_write(tx_create_chapter_version, hash_value=hash_val)
            print(f"[OK] Work/Chapter/ChapterVersion garantidos. databaseOrigin={DB_ORIGIN}")

    # Ingestão de cenas/eventos
    if args.ingest_builtin:
        print("[INFO] Ingerindo Cap. 1 a partir do JSON embutido...")
        ingest_cap1_from_dict(BUILTIN_CAP1_JSON)

    if args.ingest_json:
        print(f"[INFO] Ingerindo Cap. 1 a partir do JSON externo: {args.ingest_json}")
        with open(args.ingest_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        ingest_cap1_from_dict(data)

    driver.close()
    print("[DONE] Execução finalizada.")

if __name__ == "__main__":
    main()
