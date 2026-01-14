from unittest.mock import MagicMock, patch
import pytest
from menir_core.scribe.engine import ScribeEngine, PrivacyRouter

def test_privacy_router():
    router = PrivacyRouter()
    assert router.is_safe("fiction") == True
    assert router.is_safe("personal_creative") == True
    assert router.is_safe("legal") == False
    assert router.is_safe("ITAU") == False

@patch("menir_core.scribe.engine.NarrativeAgent")
def test_scribe_initialization_restricted(mock_agent_cls):
    # Should NOT initialize agent for restricted types
    engine = ScribeEngine(project_type="legal")
    assert engine.agent is None
    # Mock agent should not be called
    mock_agent_cls.assert_not_called()

@patch("menir_core.scribe.engine.NarrativeAgent")
def test_scribe_initialization_safe(mock_agent_cls):
    # Should initialize agent for safe types
    engine = ScribeEngine(project_type="fiction")
    assert engine.agent is not None
    mock_agent_cls.assert_called_once()

@patch("menir_core.scribe.engine.NarrativeAgent")
def test_generate_proposal_success(mock_agent_cls):
    # Setup mock agent
    mock_agent = MagicMock()
    mock_agent_cls.return_value = mock_agent
    
    # Mock response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"nodes": [], "relationships": []}'
    mock_agent.client.chat.completions.create.return_value = mock_response
    
    engine = ScribeEngine(project_type="fiction")
    result = engine.generate_proposal("Once upon a time...")
    
    assert result["status"] == "success"
    assert "proposal" in result
    assert result["proposal"] == {"nodes": [], "relationships": []}

def test_generate_proposal_skipped():
    engine = ScribeEngine(project_type="legal")
    result = engine.generate_proposal("Sensitive text")
    
    assert result["status"] == "skipped"
    assert "Privacy restrictions" in result["reason"]
