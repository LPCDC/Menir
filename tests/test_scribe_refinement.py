import json
from unittest.mock import MagicMock, patch
import pytest
from menir_core.scribe.engine import ScribeEngine
from menir_core.scribe.applicator import ScribeApplicator

def test_pii_detection():
    engine = ScribeEngine("fiction") # Safe type
    
    # 1. Clean Text
    res = engine.privacy.is_safe("fiction", "Hero walks into a bar.")
    assert res["safe"] == True
    
    # 2. CPF Detection
    res = engine.privacy.is_safe("fiction", "My CPF is 123.456.789-00")
    assert res["safe"] == False
    assert "PII" in res["reason"]
    
    # 3. Bank Keyword
    res = engine.privacy.is_safe("fiction", "Pay via Bradesco boleto.")
    assert res["safe"] == False
    assert "PII" in res["reason"]

@patch("menir_core.scribe.engine.NarrativeAgent")
def test_provenance_injection(mock_agent_cls):
    # Mock LLM
    mock_agent = MagicMock()
    mock_agent_cls.return_value = mock_agent
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"nodes": []}'
    mock_agent.client.chat.completions.create.return_value = mock_response

    engine = ScribeEngine("fiction")
    result = engine.generate_proposal("text", source_filename="chapter1.txt")
    
    assert result["status"] == "success"
    prop = result["proposal"]
    
    # Check Metadata
    assert "proposal_id" in prop
    assert prop["source"]["file"] == "chapter1.txt"
    assert prop["source"]["project"] == "fiction"
    assert "timestamp" in prop["source"]

@patch("menir_core.scribe.applicator.GraphDatabase")
def test_applicator_provenance(mock_neo4j):
    # Mock Applicator writes
    mock_driver = MagicMock()
    mock_neo4j.driver.return_value = mock_driver
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    
    app = ScribeApplicator()
    proposal = {
        "proposal_id": "test-uuid",
        "source": { "file": "test.txt", "project": "fic", "timestamp": "now" },
        "nodes": [ {"label": "Char", "properties": {"name": "Hero"}} ],
        "relationships": []
    }
    
    app.apply_proposal(proposal)
    
    # Verify provenance props in Cypher call
    args, kwargs = mock_session.run.call_args
    props = kwargs["props"]
    assert props["name"] == "Hero"
    assert props["source_file"] == "test.txt"
    assert props["proposal_id"] == "test-uuid"
