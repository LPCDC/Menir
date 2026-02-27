
import pytest
from unittest.mock import MagicMock
from src.v3.menir_runner import MenirRunner
from src.v3.schema import Person
from pydantic import ValidationError

def test_runner_partial_failure(mock_bridge):
    """
    Simulate Intel returning one valid node and one invalid node.
    The Runner should ingest the valid one and skip the invalid one without crashing.
    """
    runner = MenirRunner()
    runner.bridge = mock_bridge
    
    # Mock Logger to verify warnings
    runner_logger = MagicMock()
    
    # Input Payload
    payload = {
        "nodes": [
            {"label": "Person", "name": "ValidUser", "properties": {"role": "Tester"}},
            {"label": "Person", "properties": {"role": "Ghost"}} # Invalid: Missing Name
        ],
        "edges": []
    }
    
    # Execute
    runner.ingest_payload(payload, project="Test", doc_hash="123")
    
    # Verification
    # 1. merge_node should be called ONCE (for ValidUser)
    # Note: ingest_payload iterates nodes.
    # It calls merge_node(node_obj).
    # mock_bridge.merge_node is a MagicMock.
    
    assert mock_bridge.merge_node.call_count == 1
    args, _ = mock_bridge.merge_node.call_args
    ingested_node = args[0]
    
    assert isinstance(ingested_node, Person)
    assert ingested_node.name == "ValidUser"

