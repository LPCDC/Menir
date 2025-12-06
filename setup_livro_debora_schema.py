#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup do schema v2 para Livro Débora + utilitários básicos de ingestão.
Designed for Neo4j + Python driver; pronto para rodar localmente. Credenciais podem ser sobrescritas via env vars.
"""

import os
import hashlib
from neo4j import GraphDatabase, basic_auth

### CONFIGURAÇÃO DE ACESSO (sobreponível via env vars) ###
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "menir123")
NEO4J_DB = os.getenv("NEO4J_DB") or None  # Deixe None para usar o default 'neo4j'

### DRIVER ###
auth = basic_auth(NEO4J_USER, NEO4J_PASSWORD)
driver = GraphDatabase.driver(NEO4J_URI, auth=auth)

def open_session():
    if NEO4J_DB:
        return driver.session(database=NEO4J_DB)
    return driver.session()

def init_schema():
    schema_statements = [
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
    with open_session() as sess:
        for stmt in schema_statements:
            try:
                sess.run(stmt)
            except Exception as e:
                print(f"[WARN] Erro ao aplicar esquema: {stmt}\n → {e}")
    print("[OK] Schema v2 aplicado / atualizado com constraints & índices.")

def compute_hash_file(path, algo="sha256"):
    if not os.path.exists(path):
        print(f"[ERRO] Arquivo não encontrado: {path}")
        return None
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

### Funções utilitárias para criação de nós ###

def create_work(tx, work_id, title, author_alias, status="draft"):
    tx.run(
        "MERGE (w:Work {id: $id}) "
        "SET w.title = $title, w.authorAlias = $authorAlias, w.status = $status, "
        "    w.createdAt = coalesce(w.createdAt, datetime()), w.updatedAt = datetime()",
        id=work_id, title=title, authorAlias=author_alias, status=status
    )

def create_chapter(tx, chapter_id, number, title, short_slug=None):
    tx.run(
        "MERGE (c:Chapter {id: $id}) "
        "SET c.number = $number, c.title = $title, c.shortSlug = $shortSlug, c.updatedAt = datetime()",
        id=chapter_id, number=number, title=title, shortSlug=short_slug
    )

def create_chapter_version(tx, version_id, chapter_id, version_tag, source_type, hash_value, is_canonical=True, source_file_path=None):
    tx.run(
        "MATCH (c:Chapter {id: $chapterId}) "
        "MERGE (v:ChapterVersion {id: $id}) "
        "SET v.versionTag = $versionTag, v.sourceType = $sourceType, v.hash = $hashVal, "
        "    v.isCanonical = $isCanonical, v.sourceFilePath = $sourceFilePath, "
        "    v.createdAt = coalesce(v.createdAt, datetime()), v.updatedAt = datetime() "
        "MERGE (v)-[:VERSION_OF]->(c)",
        chapterId=chapter_id,
        id=version_id,
        versionTag=version_tag,
        sourceType=source_type,
        hashVal=hash_value,
        isCanonical=is_canonical,
        sourceFilePath=source_file_path
    )

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Neo4j setup & ingestion helper (Livro Débora)")
    parser.add_argument("--init-schema", action="store_true", help="Cria constraints / índices iniciais no banco")
    parser.add_argument("--new-work", nargs=3, metavar=("WORK_ID","TITLE","AUTHOR_ALIAS"), help="Cria ou atualiza nó Work")
    parser.add_argument("--new-chapter", nargs=3, metavar=("CH_ID","NUMBER","TITLE"), help="Cria ou atualiza nó Chapter")
    parser.add_argument("--new-chapter-version", nargs=3, metavar=("CH_ID","VERSION_TAG","PATH_TO_FILE"), help="Cria ChapterVersion a partir de arquivo")

    args = parser.parse_args()
    
    # Se nenhum argumento for passado, imprime o help
    if not any(vars(args).values()):
        parser.print_help()
        exit(0)

    try:
        # Testa conexão antes de tudo
        driver.verify_connectivity()
        
        if args.init_schema:
            init_schema()

        if args.new_work:
            with open_session() as sess:
                sess.execute_write(create_work, args.new_work[0], args.new_work[1], args.new_work[2])
                print(f"[OK] Work {args.new_work[0]} criado/atualizado.")

        if args.new_chapter:
            with open_session() as sess:
                sess.execute_write(create_chapter, args.new_chapter[0], int(args.new_chapter[1]), args.new_chapter[2])
                print(f"[OK] Chapter {args.new_chapter[0]} criado/atualizado.")

        if args.new_chapter_version:
            ch_id, ver_tag, path_file = args.new_chapter_version
            file_hash = compute_hash_file(path_file)
            if file_hash:
                version_id = f"{ch_id}_{ver_tag}"
                with open_session() as sess:
                    sess.execute_write(create_chapter_version, version_id, ch_id, ver_tag, "file", file_hash, True, path_file)
                    print(f"[OK] ChapterVersion {version_id} criado (hash={file_hash}).")
            else:
                 print("[ERRO] Hash não calculado, operação abortada.")

    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha na execução: {e}")
    finally:
        driver.close()
