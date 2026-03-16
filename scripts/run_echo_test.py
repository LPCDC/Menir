import asyncio
import json
import os
import time
import logging
from neo4j import GraphDatabase
from src.v3.menir_intel import MenirIntel
from src.v3.skills.document_classifier_skill import DocumentClassifierSkill
from src.v3.core.schemas.identity import TenantContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EchoTest")

async def run_echo_test():
    TenantContext.set("BECO")
    
    # Configurar Neo4j (credenciais via ENV como padrão do sistema)
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "neo4j")
    
    intel = MenirIntel()
    classifier = DocumentClassifierSkill(intel)
    
    test_dir = os.path.join("tests", "fixtures", "echo_test")
    files = ["IMG_4587.pdf", "scan_001.pdf", "document.pdf"]
    
    report = []
    
    start_time = time.time()
    
    processed = 0
    high_confidence = 0
    quarantine_count = 0
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    for filename in files:
        file_path = os.path.join(test_dir, filename)
        logger.info(f"Processando {filename}...")
        
        classification = await classifier.classify_document(file_path)
        processed += 1
        
        client_name = classification.suggested_client_name
        client_uid = None
        matched_name = None
        
        if client_name:
            # Busca no Neo4j com leve fuzzy/contains
            with driver.session() as session:
                query = """
                MATCH (c:ClientNode)
                WHERE toLower(c.name) CONTAINS toLower($name)
                   OR toLower($name) CONTAINS toLower(c.name)
                RETURN c.uid as uid, c.name as name
                LIMIT 1
                """
                res = session.run(query, name=client_name).single()
                if res:
                    client_uid = res["uid"]
                    matched_name = res["name"]
                    logger.info(f"Match encontrado: {matched_name} ({client_uid})")
        
        is_quarantine = classification.confidence < 0.7
        if not is_quarantine:
            high_confidence += 1
        else:
            quarantine_count += 1
            
        report.append({
            "original_filename": filename,
            "document_type": classification.document_type,
            "suggested_client_name": matched_name or client_name,
            "suggested_client_uid": client_uid,
            "confidence": classification.confidence,
            "path_to_quarantine": is_quarantine
        })
        
    driver.close()
    
    total_time = time.time() - start_time
    
    # Salvar relatório
    output_dir = os.path.join("scripts", "output")
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "echo_report_beco.json")
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
        
    print("\n" + "="*40)
    print("      ECHO TEST SUMMARY REPORT")
    print("="*40)
    print(f"Total processado:      {processed}")
    print(f"Match (> 0.7):         {high_confidence}")
    print(f"Para Quarentena:       {quarantine_count}")
    print(f"Tempo total (s):       {total_time:.2f}")
    print("="*40)
    print(f"Relatório gerado em: {report_path}")
    print("="*40 + "\n")

if __name__ == "__main__":
    asyncio.run(run_echo_test())
