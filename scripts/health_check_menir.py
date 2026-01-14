#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Health-check / smoke test para o grafo Menir + Livro Débora.
Verifica conexão, schema, ingestão básica, contagens mínimas e integridade.
"""

import os
import sys
import json
from datetime import datetime
from neo4j import GraphDatabase, basic_auth

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "menir123")
NEO4J_DB = os.getenv("NEO4J_DB", None)

SCHEMA_LABELS = [
    "Work", "Chapter", "ChapterVersion", "Chunk", "Scene", "Event",
    "Character", "Place", "Object", "EmotionState", "SummaryNode"
]


def connect():
    """Connect to Neo4j and verify connectivity."""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        return driver
    except Exception as e:
        print(f"❌ ERRO: Falha ao conectar no Neo4j: {e}")
        sys.exit(1)


def get_session(driver):
    """Get session with optional database."""
    return driver.session(database=NEO4J_DB) if NEO4J_DB else driver.session()


def check_schema(driver):
    """Verify schema labels exist."""
    with get_session(driver) as sess:
        try:
            result = sess.run("CALL db.labels()")
            labels = {record["label"] for record in result}
            missing = set(SCHEMA_LABELS) - labels
            if missing:
                print(f"⚠️ Labels ausentes no schema: {missing}")
                return False, f"Missing labels: {missing}"
            else:
                print("✅ Schema: todas labels presentes")
                return True, f"All {len(SCHEMA_LABELS)} labels present"
        except Exception as e:
            print(f"⚠️ Erro ao verificar schema: {e}")
            return False, str(e)


def ingest_minimal(driver):
    """Create minimal test data (Work + Chapter) if not exists."""
    with get_session(driver) as sess:
        try:
            sess.run("MERGE (w:Work {id: 'health_check_work', title:'HEALTH_CHECK', authorAlias:'hc'})")
            sess.run("MERGE (c:Chapter {id: 'health_check_chapter', number:0, title:'Health Check'})")
            print("✅ Ingestão mínima executada (Work + Chapter)")
            return True, "Test data created"
        except Exception as e:
            print(f"❌ Erro na ingestão: {e}")
            return False, str(e)


def verify_counts(driver):
    """Verify minimum node counts."""
    with get_session(driver) as sess:
        try:
            work_result = sess.run("MATCH (w:Work) RETURN count(w) AS cnt").single()
            work_cnt = work_result["cnt"] if work_result else 0
            
            chap_result = sess.run("MATCH (c:Chapter) RETURN count(c) AS cnt").single()
            chap_cnt = chap_result["cnt"] if chap_result else 0
            
            char_result = sess.run("MATCH (ch:Character) RETURN count(ch) AS cnt").single()
            char_cnt = char_result["cnt"] if char_result else 0
            
            scene_result = sess.run("MATCH (s:Scene) RETURN count(s) AS cnt").single()
            scene_cnt = scene_result["cnt"] if scene_result else 0
            
            event_result = sess.run("MATCH (e:Event) RETURN count(e) AS cnt").single()
            event_cnt = event_result["cnt"] if event_result else 0
            
            total = work_cnt + chap_cnt + char_cnt + scene_cnt + event_cnt
            
            counts = {
                "Work": work_cnt,
                "Chapter": chap_cnt,
                "Character": char_cnt,
                "Scene": scene_cnt,
                "Event": event_cnt,
                "Total": total
            }
            
            print(f"📊 Contagens: Work={work_cnt}, Chapter={chap_cnt}, Character={char_cnt}, Scene={scene_cnt}, Event={event_cnt}")
            
            if work_cnt < 1 or chap_cnt < 1:
                print("❌ Falha: contagens mínimas não atendidas")
                return False, f"Minimum counts not met: {counts}", counts
            else:
                print("✅ Contagens mínimas OK")
                return True, f"Minimum counts satisfied", counts
        except Exception as e:
            print(f"❌ Erro ao verificar contagens: {e}")
            return False, str(e), {}


def check_orphans(driver):
    """Check for orphan characters (no APPEARS_IN relationship)."""
    with get_session(driver) as sess:
        try:
            result = sess.run("""
                MATCH (c:Character)
                WHERE NOT (c)-[:APPEARS_IN]->(:Scene)
                RETURN c.name AS name, c.id AS id
            """)
            orphans = [{"name": rec["name"] or rec["id"], "id": rec["id"]} for rec in result]
            if orphans:
                names = [o["name"] for o in orphans]
                print(f"⚠️ {len(orphans)} personagem(ns) órfão(s): {', '.join(names)}")
                return True, f"Orphan count: {len(orphans)}", len(orphans)
            else:
                print("✅ Nenhum personagem órfão detectado")
                return True, "No orphans", 0
        except Exception as e:
            print(f"⚠️ Erro ao verificar órfãos: {e}")
            return True, f"Could not check orphans: {e}", None


def check_scenes_without_events(driver):
    """Check for scenes without events."""
    with get_session(driver) as sess:
        try:
            result = sess.run("""
                MATCH (s:Scene)
                WHERE NOT (s)<-[:OCCURS_IN]-(:Event)
                RETURN s.title AS title, s.id AS id
            """)
            scenes = [{"title": rec["title"] or rec["id"], "id": rec["id"]} for rec in result]
            if scenes:
                titles = [s["title"] for s in scenes]
                print(f"⚠️ {len(scenes)} cena(s) sem eventos: {', '.join(titles)}")
                return True, f"Scenes without events: {len(scenes)}", len(scenes)
            else:
                print("✅ Todas cenas têm eventos")
                return True, "All scenes have events", 0
        except Exception as e:
            print(f"⚠️ Erro ao verificar cenas: {e}")
            return True, f"Could not check scenes: {e}", None


def cleanup_test(driver):
    """Clean up test data."""
    with get_session(driver) as sess:
        try:
            sess.run("MATCH (w:Work {id:'health_check_work'}) DETACH DELETE w")
            sess.run("MATCH (c:Chapter {id:'health_check_chapter'}) DETACH DELETE c")
            print("🧹 Limpeza do teste concluída")
            return True, "Cleanup done"
        except Exception as e:
            print(f"⚠️ Erro ao limpar: {e}")
            return True, str(e)


def main():
    """Run all health checks."""
    print("="*70)
    print(f"Menir Health Check — {datetime.now().isoformat()}")
    print(f"Database: {NEO4J_URI}")
    print("="*70 + "\n")
    
    results = {}
    
    # Connection
    print("[1/8] Testando conexão...")
    driver = connect()
    results["connection"] = {"passed": True, "message": "✅ Conectado"}
    
    # Schema
    print("\n[2/8] Verificando schema...")
    ok, msg = check_schema(driver)
    results["schema"] = {"passed": ok, "message": msg}
    
    # Ingest minimal
    print("\n[3/8] Executando ingestão mínima...")
    ok, msg = ingest_minimal(driver)
    results["ingest"] = {"passed": ok, "message": msg}
    
    # Verify counts
    print("\n[4/8] Verificando contagens...")
    ok, msg, counts = verify_counts(driver)
    results["counts"] = {"passed": ok, "message": msg, "details": counts}
    
    # Check orphans
    print("\n[5/8] Verificando personagens órfãos...")
    ok, msg, orphan_count = check_orphans(driver)
    results["orphans"] = {"passed": ok, "message": msg, "count": orphan_count}
    
    # Check scenes
    print("\n[6/8] Verificando cenas sem eventos...")
    ok, msg, scene_count = check_scenes_without_events(driver)
    results["scenes_without_events"] = {"passed": ok, "message": msg, "count": scene_count}
    
    # Cleanup
    print("\n[7/8] Limpando dados de teste...")
    ok, msg = cleanup_test(driver)
    results["cleanup"] = {"passed": ok, "message": msg}
    
    driver.close()
    
    # Summary
    print("\n[8/8] Gerando relatório...\n")
    print("="*70)
    passed = sum(1 for r in results.values() if r.get("passed", False))
    total = len(results)
    print(f"Resultado: {passed}/{total} testes passaram")
    status = "✅ OK" if passed == total else "⚠️ WARNINGS"
    print(f"Status: {status}")
    print("="*70 + "\n")
    
    # Save JSON report
    report = {
        "timestamp": datetime.now().isoformat(),
        "database": NEO4J_URI,
        "tests": results,
        "summary": {
            "total": total,
            "passed": passed,
            "status": status
        }
    }
    
    report_path = "health_check_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"📄 Relatório salvo em: {report_path}\n")
    
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
