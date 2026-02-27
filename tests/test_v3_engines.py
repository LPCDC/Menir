"""
Pytest Suite for Menir V3 Cognitive Engines (Horizon 2 & 3)
Focuses on structurally verifying the validation pipelines without hitting production DB.
"""

import pytest
import os
import json
from src.v3.tenant_middleware import current_tenant_id, SecurityViolationError
from src.v3.shacl_validator import RulebookOtani
from src.v3.ingestion_engine import ValidatorStage, DocumentSchema, ChunkSchema
from pydantic import ValidationError

# --- 1. Tenant Middleware Tests ---
def test_tenant_context_manager():
    """Verify that current_tenant_id correctly sets and resets."""
    token = current_tenant_id.set("TEST_TENANT")
    assert current_tenant_id.get() == "TEST_TENANT"
    
    current_tenant_id.reset(token)
    assert current_tenant_id.get() is None

# --- 2. SHACL Validator Tests ---
def test_shacl_cypher_generation():
    """Ensure Otani cypher string rules are syntactically valid."""
    rule1 = RulebookOtani.get_corridor_width_rule()
    assert "MATCH (c:Corridor)" in rule1
    assert "WHERE c.width < 1.20" in rule1
    
    rule2 = RulebookOtani.get_maximum_exit_distance_rule(20.0)
    assert "WHERE total_dist > 20.0" in rule2

# --- 3. Ingestion Engine (Pydantic) Tests ---
def test_document_schema_validation():
    """Test Stage 2 Pydantic Validation for Documents."""
    valid_doc = {
        "type": "Document",
        "sha256": "abcdef123456",
        "filename": "test.pdf",
        "filepath": "/docs/test.pdf",
        "size_bytes": 1024,
        "extension": ".pdf",
        "project": "VITAL"
    }
    
    # Should not raise
    doc = DocumentSchema(**valid_doc)
    assert doc.sha256 == "abcdef123456"

    # Should raise due to missing 'project'
    invalid_doc = valid_doc.copy()
    del invalid_doc["project"]
    
    with pytest.raises(ValidationError):
        DocumentSchema(**invalid_doc)

def test_chunk_schema_validation():
    """Test Stage 2 Pydantic Validation for Chunks."""
    valid_chunk = {
        "type": "Chunk",
        "uid": "uuid-1234",
        "text": "This is a chunk.",
        "embedding": [0.1, 0.2, 0.3],
        "index": 0,
        "source_sha256": "abcdef123456",
        "project": "VITAL"
    }
    
    chunk = ChunkSchema(**valid_chunk)
    assert chunk.index == 0
    assert len(chunk.embedding) == 3

def test_dlq_routing(tmp_path):
    """Test that ValidatorStage correctly routes bad lines to DLQ."""
    raw_file = tmp_path / "raw.jsonl"
    val_file = tmp_path / "val.jsonl"
    dlq_file = tmp_path / "dlq.jsonl"
    
    # Write 1 valid doc and 1 invalid chunk to raw
    with open(raw_file, "w") as f:
        f.write('{"type": "Document", "sha256": "hash", "filename": "a.txt", "filepath": "a", "size_bytes": 10, "extension": ".txt", "project": "P1"}\n')
        f.write('{"type": "Chunk", "uid": "123", "text": "bad chunk"} \n') # Missing embedding, project, etc
        
    validator = ValidatorStage()
    validator.validate(str(raw_file), str(val_file), str(dlq_file))
    
    # Check valid output
    with open(val_file, "r") as f:
        val_lines = f.readlines()
        assert len(val_lines) == 1
        assert "Document" in val_lines[0]
        
    # Check DLQ output
    with open(dlq_file, "r") as f:
        dlq_lines = f.readlines()
        assert len(dlq_lines) == 1
        dlq_data = json.loads(dlq_lines[0])
        assert "error" in dlq_data
        assert dlq_data["payload"]["uid"] == "123"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
