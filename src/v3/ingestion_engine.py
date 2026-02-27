"""
Menir Ingestion Engine (Horizon 2 - 4-stage Pipeline)
1. Extract & Normalize (JSONL)
2. Schema Enforcement (Pydantic & DLQ)
3. Batch Loading (UNWIND)
4. Post-Ingest Hooks (Signatures)
"""
import logging
import os
import uuid
import hashlib
import json
from typing import List, Dict, Any
from datetime import datetime, timezone
from dotenv import load_dotenv
import google.generativeai as genai
from pydantic import BaseModel, ValidationError

from src.v3.menir_bridge import MenirBridge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IngestionEngine")
load_dotenv()

# ==========================================
# Schema Definitions (Stage 2)
# ==========================================
class DocumentSchema(BaseModel):
    sha256: str
    filename: str
    filepath: str
    size_bytes: int
    extension: str
    project: str
    type: str = "Document"

class ChunkSchema(BaseModel):
    uid: str
    text: str
    embedding: List[float]
    index: int
    source_sha256: str
    project: str
    type: str = "Chunk"


# ==========================================
# Stage 1: Extraction & Normalization
# ==========================================
from src.v3.local_embedder import EdgeEmbedder

class ExtractorStage:
    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.embedder = EdgeEmbedder()

    def process_to_jsonl(self, filepath: str, project: str, output_path: str):
        logger.info(f"[Stage 1] Extracting & Normalizing: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        sha256 = hashlib.sha256(content.encode()).hexdigest()
        filename = os.path.basename(filepath)
        
        doc_record = {
            "type": "Document",
            "sha256": sha256,
            "filename": filename,
            "filepath": filepath,
            "size_bytes": len(content),
            "extension": os.path.splitext(filename)[1],
            "project": project
        }

        records = [doc_record]
        
        start = 0
        text_len = len(content)
        idx = 0
        while start < text_len:
            end = start + self.chunk_size
            text = content[start:end]
            vector = self.embedder.embed(text)
            records.append({
                "type": "Chunk",
                "uid": str(uuid.uuid4()),
                "text": text,
                "embedding": vector,
                "index": idx,
                "source_sha256": sha256,
                "project": project
            })
            start += self.chunk_size - self.overlap
            idx += 1

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            for r in records:
                f.write(json.dumps(r) + '\n')
        
        logger.info(f"[Stage 1] Wrote {len(records)} records to {output_path}")


# ==========================================
# Stage 2: Schema Enforcement
# ==========================================
class ValidatorStage:
    def validate(self, input_jsonl: str, valid_jsonl: str, dlq_jsonl: str):
        logger.info(f"[Stage 2] Enforcing Schema for {input_jsonl}")
        valid_count = 0
        dlq_count = 0
        
        with open(input_jsonl, 'r', encoding='utf-8') as fin, \
             open(valid_jsonl, 'w', encoding='utf-8') as fval, \
             open(dlq_jsonl, 'w', encoding='utf-8') as fdlq:
             
            for line in fin:
                if not line.strip(): continue
                data = json.loads(line)
                try:
                    if data.get('type') == 'Document':
                        DocumentSchema(**data)
                    elif data.get('type') == 'Chunk':
                        ChunkSchema(**data)
                    else:
                        raise ValueError(f"Unknown record type: {data.get('type')}")
                    
                    fval.write(line)
                    valid_count += 1
                except (ValidationError, ValueError) as e:
                    dlq_record = {"error": str(e), "payload": data}
                    fdlq.write(json.dumps(dlq_record) + '\n')
                    dlq_count += 1
                    
        logger.info(f"[Stage 2] Valid: {valid_count}, DLQ: {dlq_count}")


# ==========================================
# Stage 3: Batch Loading (UNWIND)
# ==========================================
class BatchLoaderStage:
    def __init__(self, bridge: MenirBridge):
        self.bridge = bridge

    def load(self, valid_jsonl: str):
        logger.info(f"[Stage 3] Batch Loading (UNWIND) from {valid_jsonl}")
        docs = []
        chunks = []
        
        with open(valid_jsonl, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                data = json.loads(line)
                if data.get('type') == 'Document':
                    docs.append(data)
                elif data.get('type') == 'Chunk':
                    chunks.append(data)

        with self.bridge.driver.session() as session:
            if docs:
                doc_query = """
                UNWIND $batch AS row
                MERGE (d:Document {sha256: row.sha256, project: row.project})
                SET d.filename = row.filename, d.filepath = row.filepath, 
                    d.size_bytes = row.size_bytes, d.extension = row.extension,
                    d.ingested_at = datetime()
                """
                session.run(doc_query, batch=docs)
                logger.info(f"[Stage 3] Merged {len(docs)} Documents")

            if chunks:
                chunk_query = """
                UNWIND $batch AS row
                MERGE (c:Chunk {uid: row.uid})
                SET c.text = row.text, c.embedding = row.embedding, c.index = row.index,
                    c.project = row.project, c.generated_at = datetime()
                WITH c, row
                MATCH (d:Document {sha256: row.source_sha256, project: row.project})
                MERGE (d)-[:HAS_CHUNK]->(c)
                """
                session.run(chunk_query, batch=chunks)
                logger.info(f"[Stage 3] Merged {len(chunks)} Chunks")


# ==========================================
# Stage 4: Post-Ingest Hooks
# ==========================================
class HookStage:
    def __init__(self, bridge: MenirBridge):
        self.bridge = bridge

    def sign_batch(self, valid_jsonl: str, project: str):
        logger.info("[Stage 4] Generating Cryptographic Signature for Batch")
        with open(valid_jsonl, 'rb') as f:
            batch_hash = hashlib.sha256(f.read()).hexdigest()
            
        timestamp = datetime.now(timezone.utc).isoformat()
        receipt = {
            "batch_hash": batch_hash,
            "timestamp": timestamp,
            "project": project,
            "status": "SUCCESS"
        }
        
        query = """
        MERGE (l:IngestLog {batch_hash: $batch_hash})
        SET l.timestamp = $timestamp, l.project = $project, l.status = $status
        """
        with self.bridge.driver.session() as session:
            session.run(query, **receipt)
            
        logger.info(f"[Stage 4] Batch Signature {batch_hash[:8]} committed.")


# ==========================================
# Orchestrator Pipeline
# ==========================================
class IngestionPipeline:
    def __init__(self):
        self.bridge = MenirBridge()
        self.extractor = ExtractorStage()
        self.validator = ValidatorStage()
        self.loader = BatchLoaderStage(self.bridge)
        self.hooks = HookStage(self.bridge)

    def run(self, filepath: str, project: str = "MenirVital"):
        raw_jsonl = f"staging/{os.path.basename(filepath)}.raw.jsonl"
        val_jsonl = f"staging/{os.path.basename(filepath)}.valid.jsonl"
        dlq_jsonl = f"staging/{os.path.basename(filepath)}.dlq.jsonl"
        
        # In order to let MenirBridge's Driver work natively, we set the tenant_id in context if we use Middleware
        try:
            from src.v3.tenant_middleware import current_tenant_id
            t = current_tenant_id.set(project)
        except ImportError:
            t = None

        try:
            self.extractor.process_to_jsonl(filepath, project, raw_jsonl)
            self.validator.validate(raw_jsonl, val_jsonl, dlq_jsonl)
            self.loader.load(val_jsonl)
            self.hooks.sign_batch(val_jsonl, project)
            logger.info("🎯 Pipeline completed successfully.")
        finally:
            if t is not None:
                current_tenant_id.reset(t)
            self.bridge.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Menir Ingestion Engine (4-Stage Pipeline)")
    parser.add_argument("--file", required=True, help="Path to text file to ingest")
    parser.add_argument("--project", default="MenirVital", help="Project namespace")
    
    args = parser.parse_args()
    
    pipeline = IngestionPipeline()
    pipeline.run(args.file, args.project)
