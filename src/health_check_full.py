#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menir — Full Health & Sanity Check / Smoke Test

Verifica conexão, schema, ingestão mínima, contagens básicas,
integridade mínima (ex: cenas têm eventos, sem dados órfãos críticos),
gera relatório JSON e limpa dados de teste.
"""

import os
import sys
import json
from datetime import datetime
from neo4j import GraphDatabase, basic_auth

# Configuração via ambiente ou default
NEO4J_URI      = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER     = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "menir123")
REPORT_PATH   = os.getenv("MENIR_FULL_CHECK_REPORT", "menir_full_check_report.json")

EXPECTED_LABELS = [
    "Work", "Chapter", "ChapterVersion", "Chunk",
    "Scene", "Event", "Character", "Place",
    "Object", "EmotionState", "SummaryNode"
]


def connect_db():
    """Connect to Neo4j database."""
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD)
        )
        driver.verify_connectivity()
        return driver, None
    except Exception as e:
        return None, str(e)


def get_existing_labels(driver):
    """Get all labels from database."""
    with driver.session() as session:
        result = session.run("CALL db.labels()")
        return {record["label"] for record in result}


def ingest_minimal(driver):
    """Create minimal test nodes."""
    with driver.session() as sess:
        sess.run("""
          MERGE (w:Work {id: 'health_test_work', title: 'TEST_WORK', authorAlias: 'health_check'})
          MERGE (c:Chapter {id: 'health_test_chapter', number: 0, title: 'TEST_CHAPTER'})
        """)
    return True


def count_label(driver, label):
    """Count nodes with given label."""
    with driver.session() as s:
        r = s.run(f"MATCH (n:`{label}`) RETURN count(n) AS c").single()
        return r["c"] if r else 0


def cleanup_test_nodes(driver):
    """Clean up test data."""
    with driver.session() as s:
        s.run("MATCH (w:Work {id:'health_test_work'}) DETACH DELETE w")
        s.run("MATCH (c:Chapter {id:'health_test_chapter'}) DETACH DELETE c")


def basic_integrity_checks(driver):
    """Check for data integrity issues."""
    with driver.session() as s:
        # Check: cada Scene deve ter pelo menos 1 Evento
        missing = []
        q = """
        MATCH (s:Scene)
        WHERE NOT EXISTS { (s)<-[:OCCURS_IN]-(:Event) }
        RETURN s.id AS sceneId
        """
        for rec in s.run(q):
            missing.append(rec["sceneId"])
    return missing


def run_full_check():
    """Run complete health check."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "neo4j_uri": NEO4J_URI,
        "schema": {},
        "counts": {},
        "integrity": {},
        "status": None
    }

    driver, err = connect_db()
    if not driver:
        report["status"] = "ERROR"
        report["error"] = f"Connection failed: {err}"
        return report

    labels = get_existing_labels(driver)
    missing_lbl = set(EXPECTED_LABELS) - labels
    extra_lbl = labels - set(EXPECTED_LABELS)
    report["schema"]["missing_labels"] = sorted(list(missing_lbl))
    report["schema"]["extra_labels"] = sorted(list(extra_lbl))

    ingest_minimal(driver)

    for lbl in ["Work", "Chapter", "Character", "Scene", "Event"]:
        report["counts"][lbl] = count_label(driver, lbl)

    orphan_scenes = basic_integrity_checks(driver)
    report["integrity"]["scenes_without_events"] = orphan_scenes

    cleanup_test_nodes(driver)

    report["status"] = "OK" if not missing_lbl else "WARN"

    driver.close()
    return report


def main():
    """Main execution."""
    rep = run_full_check()
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2, ensure_ascii=False)

    print("Menir Full Check Report —", rep["timestamp"])
    if rep.get("error"):
        print("❌ ERRO:", rep["error"])
        sys.exit(1)

    if rep["schema"]["missing_labels"]:
        print("⚠️ Labels ausentes:", rep["schema"]["missing_labels"])
    else:
        print("✅ Schema OK")

    print("📊 Contagens principais:", rep["counts"])

    if rep["integrity"]["scenes_without_events"]:
        print("⚠️ Cenas sem eventos:", rep["integrity"]["scenes_without_events"])
    else:
        print("✅ Todas cenas têm eventos")

    if rep["status"] == "OK":
        print("✅ FULL CHECK PASSED")
        sys.exit(0)
    else:
        print("⚠️ FULL CHECK warning — revisar relatório")
        sys.exit(1)


if __name__ == "__main__":
    main()
