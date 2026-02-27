import json
import sys
import os

# Ensure we can import menir_core
sys.path.append("/app")
from menir_core.governance.sanitizer import LGPDSanitizer

def generate():
    sanitizer = LGPDSanitizer()
    
    # Raw Data Samples
    raw_data = [
        "Transferência de R$ 500,00 para Joao Silva referente a aluguel.",
        "Pix recebido de Maria Eduarda Souza confirmado.",
        "Boleto de Carlos Drummond liquidado.",
        "Acesso de admin por Pedro Alvares.",
        "Log de erro: Timeout na conta de Ana Clara."
    ]
    
    chunks = []
    for snippet in raw_data:
        masked = sanitizer.mask_pii(snippet)
        chunks.append(masked)
        
    # Construct Operations
    ops = []
    
    # 1. Project/Task Ensure (Redundant but safe)
    ops.append({
        "op_id": "ensure_itau_structure",
        "description": "Ensure Itaú Project Structure Exists",
        "cypher": "MERGE (p:Project {id:'itau_15220012'}) SET p.name='Itaú Data Sanitization', p.priority='high' RETURN p"
    })
    
    # 2. Ingest Chunks
    for idx, text in enumerate(chunks):
        op = {
            "op_id": f"ingest_chunk_{idx}",
            "description": f"Ingest Sanitized Log {idx}",
            "cypher": f"MATCH (p:Project {{id:'itau_15220012'}}) CREATE (d:Document {{id:'doc:itau:{idx}'}}) SET d.text = '{text}', d.status='sanitized', d.project='Itaú' MERGE (p)-[:HAS_DOCUMENT]->(d) RETURN d"
        }
        ops.append(op)
        
    proposal = {
        "meta": {
            "proposal_id": "ITAU_SANITIZED_BATCH_001",
            "project": "Itaú-15220012",
            "dry_run": False
        },
        "operations": ops
    }
    
    output_path = "/app/scripts/backlog_itau.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(proposal, f, indent=2, ensure_ascii=False)
        
    print(f"Generated {output_path} with {len(chunks)} chunks.")

if __name__ == "__main__":
    generate()
