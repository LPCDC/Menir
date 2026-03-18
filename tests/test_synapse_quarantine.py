import pytest
import json
import jwt
import os
import uuid
from aiohttp import web
from unittest.mock import AsyncMock, MagicMock, patch
from src.v3.core.synapse import MenirSynapse
from src.v3.skills.document_classifier_skill import DocumentClassification

@pytest.fixture
def mock_runner():
    runner = MagicMock()
    runner.ontology_manager.driver.session = MagicMock()
    return runner

@pytest.fixture
def mock_intel():
    return MagicMock()

@pytest.mark.asyncio
async def test_get_quarantine_documents(mock_runner, mock_intel):
    synapse = MenirSynapse(mock_runner, mock_intel)
    
    # Mock JWT
    jwt_secret = "super_secret_menir_key_2026_replaced"
    os.environ["MENIR_JWT_SECRET"] = jwt_secret
    token = jwt.encode({"tenant_id": "BECO"}, jwt_secret, algorithm="HS256")
    
    mock_request = MagicMock(spec=web.Request)
    mock_request.headers = {"Authorization": f"Bearer {token}"}
    
    # Mock Neo4j session and records
    mock_session = MagicMock()
    mock_runner.ontology_manager.driver.session.return_value.__enter__.return_value = mock_session
    
    mock_record = MagicMock()
    mock_record.data.return_value = {
        "q": {
            "uid": "q-123",
            "name": "test.pdf",
            "document_type": "INVOICE_SUPPLIER",
            "suggested_client": "Ana Paula",
            "confidence": 0.65,
            "language": "pt"
        }
    }
    
    mock_result = MagicMock()
    mock_result.all.return_value = [mock_record]
    mock_session.run.return_value = mock_result
    
    response = await synapse.handle_get_quarantine_documents(mock_request)
    
    assert response.status == 200
    body = json.loads(response.text)
    assert len(body) == 1
    assert body[0]["uid"] == "q-123"
    assert "MATCH (q:QuarantineItem:`BECO` {status: 'PENDING'})" in mock_session.run.call_args[0][0]

@pytest.mark.asyncio
async def test_accept_quarantine_document(mock_runner, mock_intel):
    synapse = MenirSynapse(mock_runner, mock_intel)
    
    # Mock JWT
    jwt_secret = "super_secret_menir_key_2026_replaced"
    os.environ["MENIR_JWT_SECRET"] = jwt_secret
    token = jwt.encode({"tenant_id": "BECO"}, jwt_secret, algorithm="HS256")
    
    mock_request = MagicMock(spec=web.Request)
    mock_request.headers = {"Authorization": f"Bearer {token}"}
    mock_request.match_info = {"uid": "q-123"}
    
    # Mock Neo4j session
    mock_session = MagicMock()
    mock_runner.ontology_manager.driver.session.return_value.__enter__.return_value = mock_session
    
    # Pre-mocking the QuarantineItem fetch
    mock_q_data = {
        "q": {
            "uid": "q-123",
            "name": "test.pdf",
            "file_hash": "abc",
            "document_type": "INVOICE_SUPPLIER",
            "suggested_client": "Ana Paula",
            "confidence": 0.65,
            "language": "pt"
        }
    }
    
    # Mock results for multiple runs
    mock_result_fetch = MagicMock()
    mock_result_fetch.single.return_value.data.return_value = mock_q_data
    
    mock_session.run.side_effect = [mock_result_fetch, MagicMock(), MagicMock()] # Fetch, Promote, Mark Accepted
    
    with patch("src.v3.core.synapse.NodePersistenceOrchestrator.persist", new_callable=AsyncMock) as mock_persist:
        mock_persist.return_value = "new-doc-uid"
        
        response = await synapse.handle_accept_quarantine_document(mock_request)
        
        assert response.status == 200
        body = json.loads(response.text)
        assert body["status"] == "ACCEPTED"
        assert body["promoted_uid"] == "new-doc-uid"

@pytest.mark.asyncio
async def test_correct_quarantine_document(mock_runner, mock_intel):
    synapse = MenirSynapse(mock_runner, mock_intel)
    
    # Mock JWT
    jwt_secret = "super_secret_menir_key_2026_replaced"
    os.environ["MENIR_JWT_SECRET"] = jwt_secret
    token = jwt.encode({"tenant_id": "BECO"}, jwt_secret, algorithm="HS256")
    
    mock_request = MagicMock(spec=web.Request)
    mock_request.headers = {"Authorization": f"Bearer {token}"}
    mock_request.match_info = {"uid": "q-123"}
    mock_request.json = AsyncMock(return_value={"client_name": "Pierre Muller"})
    
    # Mock Neo4j session
    mock_session = MagicMock()
    mock_runner.ontology_manager.driver.session.return_value.__enter__.return_value = mock_session
    
    # Pre-mocking the QuarantineItem fetch
    mock_q_data = {
        "q": {
            "uid": "q-123",
            "name": "test.pdf",
            "file_hash": "abc",
            "document_type": "INVOICE_SUPPLIER",
            "suggested_client": "Ana Paula",
            "confidence": 0.65,
            "language": "pt"
        }
    }
    
    mock_result_fetch = MagicMock()
    mock_result_fetch.single.return_value.data.return_value = mock_q_data
    mock_session.run.side_effect = [mock_result_fetch, MagicMock(), MagicMock()]
    
    with patch("src.v3.core.synapse.NodePersistenceOrchestrator.persist", new_callable=AsyncMock) as mock_persist:
        mock_persist.return_value = "new-doc-uid-corrected"
        
        response = await synapse.handle_correct_quarantine_document(mock_request)
        
        assert response.status == 200
        body = json.loads(response.text)
        assert body["status"] == "CORRECTED"
        
        # Verify that persist was called with corrected client name in metadata
        persisted_node = mock_persist.call_args[0][0]
        assert persisted_node.metadata["suggested_client"] == "Pierre Muller"
