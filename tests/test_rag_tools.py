import json
from unittest.mock import MagicMock, patch
import pytest
from menir_core.rag.tools import query_narrative_graph, find_relevant_chunks

def test_query_narrative_graph_safety():
    """Test that dangerous keywords are blocked."""
    unsafe_queries = [
        "MATCH (n) DETACH DELETE n", 
        "CREATE (n:Person {name:'Bad'})",
        "DROP INDEX abc",
        "MERGE (n:Node)"
    ]
    for q in unsafe_queries:
        result = query_narrative_graph(q)
        data = json.loads(result)
        assert "error" in data
        assert "Write operations are not allowed" in data["error"]

@patch("menir_core.rag.tools.driver")
def test_query_narrative_graph_success(mock_driver):
    """Test successful query execution."""
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    
    # Mock result
    mock_record = MagicMock()
    mock_record.data.return_value = {"name": "Test"}
    mock_session.run.return_value = [mock_record]
    
    result = query_narrative_graph("MATCH (n) RETURN n")
    data = json.loads(result)
    
    assert isinstance(data, list)
    assert data[0]["name"] == "Test"

@patch("menir_core.rag.tools.embed_text")
@patch("menir_core.rag.tools.driver")
def test_find_relevant_chunks(mock_driver, mock_embed):
    """Test vector search logic."""
    # Mock embedding
    mock_embed.return_value = [1.0, 0.0]
    
    # Mock Neo4j return
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    
    # Chunk 1: Identical [1.0, 0.0] -> score 1.0
    # Chunk 2: Orthogonal [0.0, 1.0] -> score 0.0
    chunk1 = {"text": "A", "embedding": [1.0, 0.0], "id": 1}
    chunk2 = {"text": "B", "embedding": [0.0, 1.0], "id": 2}
    
    mock_session.run.return_value = [chunk1, chunk2]
    
    result = find_relevant_chunks("query")
    data = json.loads(result)
    
    # Should be sorted by score
    assert len(data) == 2
    assert data[0]["text"] == "A"
    assert data[0]["score"] > 0.9
    assert data[1]["text"] == "B"
    assert data[1]["score"] < 0.1
