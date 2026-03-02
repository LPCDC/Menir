#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menir / Livro Débora — Quick Health Check / Smoke Test
Testa conexão, schema, ingestão mínima, contagens e limpa teste.
Versão rápida e leve para CI/CD.
"""

import os
import sys
import json
from neo4j import GraphDatabase, basic_auth
from datetime import datetime

# Config via env ou defaults
NEO4J_URI      = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER     = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "menir123")

# Labels esperadas
EXPECTED_LABELS = [
    "Work","Chapter","ChapterVersion","Chunk",
    "Scene","Event","Character","Place",
    "Object","EmotionState","SummaryNode"
]

REPORT_PATH = os.getenv("MENIR_HEALTH_REPORT", "health_check_quick_report.json")

def connect():
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        return driver
    except Exception as e:
        print("❌ ERRO: Falha ao conectar no Neo4j:", e)
        sys.exit(1)

def check_schema(driver):
    with driver.session() as sess:
        result = sess.run("CALL db.labels()")
        labels = {r["label"] for r in result}
    missing = set(EXPECTED_LABELS) - labels
    extra   = labels - set(EXPECTED_LABELS)
    return missing, extra

def ingest_minimal(driver):
    with driver.session() as s:
        s.run("""
            MERGE (w:Work {id: 'health_test_work', title: 'TEST_WORK', authorAlias: 'health_check'})
            MERGE (c:Chapter {id: 'health_test_chapter', number: 0, title: 'TEST_CHAPTER'})
        """)
    return True

def count_nodes(driver, label):
    with driver.session() as s:
        r = s.run(f"MATCH (n:{label}) RETURN count(n) AS cnt").single()
    return r["cnt"] if r else 0

def cleanup_test(driver):
    with driver.session() as s:
        s.run("MATCH (w:Work {id:'health_test_work'}) DETACH DELETE w")
        s.run("MATCH (c:Chapter {id:'health_test_chapter'}) DETACH DELETE c")

def run_check():
    driver = connect()
    missing, extra = check_schema(driver)
    ingest_minimal(driver)
    counts = {lab: count_nodes(driver, lab) for lab in ["Work","Chapter","Character","Scene","Event"]}
    cleanup_test(driver)
    driver.close()
    return {"timestamp": datetime.now().isoformat(),
            "uri": NEO4J_URI,
            "schema_missing_labels": list(missing),
            "schema_extra_labels": list(extra),
            "counts": counts}

def main():
    report = run_check()
    ok = True

    print("=== Menir Quick Health Check ===")
    print("DB URI:", report["uri"])
    if report["schema_missing_labels"]:
        print("⚠️ Labels faltando:", report["schema_missing_labels"])
        ok = False
    else:
        print("✅ Todas labels do schema presentes")

    print("📊 Contagens mínimas:", report["counts"])
    if report["counts"].get("Work",0) < 1 or report["counts"].get("Chapter",0) < 1:
        print("❌ Contagens mínimas não atendidas")
        ok = False

    report["status"] = "OK" if ok else "FAIL"
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("📝 Relatório escrito em:", REPORT_PATH)

    if not ok:
        sys.exit(1)
    print("✅ Quick health-check completo")

if __name__ == "__main__":
    main()
