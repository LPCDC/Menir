import argparse
import csv
import json
import os
import uuid
import logging
from typing import List, Dict, Any
from neo4j import GraphDatabase
from pydantic import ValidationError

from src.v3.skills.sanitize_clients import ClientInput
from src.v3.core.schemas.identity import TenantContext

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Bootstrap BECO clients into Neo4j")
    parser.add_argument("--input", required=True, help="Path to CSV or JSON file")
    parser.add_argument("--uri", default=os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    parser.add_argument("--user", default=os.getenv("NEO4J_USER", "neo4j"))
    parser.add_argument("--password", default=os.getenv("NEO4J_PASSWORD", "neo4j"))
    return parser.parse_args()

def process_clients(file_path: str, neo4j_uri: str, neo4j_user: str, neo4j_pass: str):
    valid_clients = []
    discarded = 0
    total = 0
    
    ext = os.path.splitext(file_path)[1].lower()
    raw_data: List[Dict[str, Any]] = []
    
    try:
        if ext == ".csv":
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    raw_data.append({k: (v if v else None) for k, v in row.items()})
        elif ext == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        else:
            logger.error("Unsupported file extension. Use .csv or .json")
            return 0, 0, 0, 0
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {e}")
        return 0, 0, 0, 0
            
    total = len(raw_data)
    
    for row in raw_data:
        try:
            client = ClientInput(**row)
            
            valid_clients.append({
                "uid": str(uuid.uuid4()),
                "name": client.name,
                "client_type": client.client_type.value,
                "canton": client.canton,
                "language": client.language,
                "fiscal_id": client.fiscal_id,
                "tva_number": client.tva_number,
                "tva_status": client.tva_status
            })
        except ValidationError as e:
            logger.warning(f"Discarding invalid client row {row.get('name', 'Unknown')}: {e}")
            discarded += 1
            
    valid = len(valid_clients)
    injected = 0
    
    tenant = TenantContext.get()
    if not tenant:
        logger.error("TenantContext under execution is not set. Stopping injection.")
        return total, valid, injected, discarded
        
    tenant_safe = tenant.replace("`", "")
        
    if valid_clients:
        cypher = f"""
        UNWIND $batch AS client
        MERGE (c:ClientNode:`{tenant_safe}` {{name: client.name, canton: client.canton}})
        ON CREATE SET 
            c.uid = client.uid,
            c.client_type = client.client_type,
            c.language = client.language,
            c.fiscal_id = client.fiscal_id,
            c.tva_number = client.tva_number,
            c.tva_status = client.tva_status
        ON MATCH SET
            c.client_type = client.client_type,
            c.language = client.language,
            c.fiscal_id = client.fiscal_id,
            c.tva_number = client.tva_number,
            c.tva_status = client.tva_status
            
        MERGE (t:Tenant {{name: $tenant}})
        MERGE (c)-[:BELONGS_TO_TENANT]->(t)
        """
        
        try:
            with GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass)) as driver:
                with driver.session() as session:
                    with session.begin_transaction() as tx:
                        tx.run(cypher, batch=valid_clients, tenant=tenant_safe)
                        injected = valid
        except Exception as e:
            logger.error(f"Failed to inject valid clients into Neo4j: {e}", exc_info=True)
            
    print(f"--- BECO CLIENTS BOOTSTRAP REPORT ---")
    print(f"Lidos:      {total}")
    print(f"Validos:    {valid}")
    print(f"Injetados:  {injected}")
    print(f"Descartados:{discarded}")
    print(f"-------------------------------------")
    
    # Gerar echo_report_beco.json sintetico
    output_dir = "scripts/output"
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "echo_report_beco.json")
    
    report_data = []
    for client in valid_clients:
        report_data.append({
            "nome_arquivo": file_path,
            "cliente_encontrado": client["name"],
            "confiança": 1.0 # Sintetico por enquanto
        })
        
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4, ensure_ascii=False)
        
    return total, valid, injected, discarded

if __name__ == "__main__":
    args = parse_args()
    TenantContext.set("BECO")
    process_clients(args.input, args.uri, args.user, args.password)
