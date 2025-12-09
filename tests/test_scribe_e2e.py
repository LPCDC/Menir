import json
import os
from unittest.mock import MagicMock, patch
import pytest
from menir_core.scribe.engine import ScribeEngine
from menir_core.scribe.applicator import ScribeApplicator

@patch("menir_core.scribe.engine.NarrativeAgent")
@patch("menir_core.scribe.applicator.GraphDatabase")
def test_end_to_end_scribe(mock_neo4j, mock_agent_cls):
    """
    Test Text -> Proposal -> Graph write.
    """
    # 1. MOCK SCRIBE GENERATION
    mock_agent = MagicMock()
    mock_agent_cls.return_value = mock_agent
    
    # Simulate LLM returning a proposal
    mock_proposal_json = {
        "nodes": [
            {"label": "Character", "properties": {"name": "TestHero"}}
        ],
        "relationships": []
    }
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps(mock_proposal_json)
    mock_agent.client.chat.completions.create.return_value = mock_response

    engine = ScribeEngine(project_type="fiction")
    result = engine.generate_proposal("TestHero walks in.")
    
    assert result["status"] == "success"
    proposal = result["proposal"]
    assert proposal["nodes"][0]["properties"]["name"] == "TestHero"
    
    # 2. MOCK APPLICATOR WRITE
    mock_driver = MagicMock()
    mock_neo4j.driver.return_value = mock_driver
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    
    applicator = ScribeApplicator()
    stats = applicator.apply_proposal(proposal)
    
    # Verify session.run was called for MERGE
    assert mock_session.run.called
    args, kwargs = mock_session.run.call_args
    assert "MERGE" in args[0]
    assert "TestHero" in str(kwargs)
    assert stats["nodes_created"] == 1
