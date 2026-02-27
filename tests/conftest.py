
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_neo4j_session():
    """Mocks a Neo4j session/driver interaction."""
    session = MagicMock()
    # Default behavior: run() returns a mock Result
    mock_result = MagicMock()
    mock_result.single.return_value = {"exists": False} # Default checking for existence
    session.run.return_value = mock_result
    return session

@pytest.fixture
def mock_bridge(mock_neo4j_session):
    """Mocks the MenirBridge class."""
    with patch("src.v3.menir_bridge.MenirBridge") as MockBridge:

        instance = MockBridge.return_value
        # Mock the context manager behavior for session()
        instance.driver.session.return_value.__enter__.return_value = mock_neo4j_session
        yield instance

@pytest.fixture
def mock_intel_response():
    """Default valid Intel extraction payload."""
    return {
        "nodes": [
            {"label": "Person", "name": "Luiz", "properties": {"role": "Creator"}},
            {"label": "Document", "name": "TestDoc.pdf", "properties": {"status": "processed"}}
        ],
        "edges": []
    }
