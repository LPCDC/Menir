import pytest
import json
import io
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
async def test_classify_document_handler_direct(mock_runner, mock_intel):
    synapse = MenirSynapse(mock_runner, mock_intel)
    
    # Mock JWT
    jwt_secret = "super_secret_menir_key_2026_replaced"
    os.environ["MENIR_JWT_SECRET"] = jwt_secret
    token = jwt.encode({"tenant_id": "BECO"}, jwt_secret, algorithm="HS256")
    
    # Mock Request
    mock_request = MagicMock(spec=web.Request)
    mock_request.headers = {"Authorization": f"Bearer {token}"}
    
    # Mock Multipart Reader
    mock_field = AsyncMock()
    mock_field.name = 'file'
    mock_field.filename = 'test.pdf'
    mock_field.read_chunk = AsyncMock(side_effect=[b"%PDF-1.4 content", None])
    
    mock_multipart = AsyncMock()
    mock_multipart.next = AsyncMock(side_effect=[mock_field, None])
    mock_request.multipart = AsyncMock(return_value=mock_multipart)
    
    # Mock Skills and Persistence
    mock_classification = DocumentClassification(
        document_type="INVOICE_SUPPLIER",
        suggested_client_name="Ana Paula",
        confidence=0.95,
        language="pt"
    )
    
    with patch("src.v3.core.synapse.DocumentClassifierSkill.classify_document", new_callable=AsyncMock) as mock_classify, \
         patch("src.v3.core.synapse.NodePersistenceOrchestrator.persist", new_callable=AsyncMock) as mock_persist:
        
        mock_classify.return_value = mock_classification
        mock_persist.return_value = "doc-uid-123"
        
        response = await synapse.handle_classify_document(mock_request)
        
        assert response.status == 200
        body = json.loads(response.text)
        assert body["document_type"] == "INVOICE_SUPPLIER"
        assert body["uid"] == "doc-uid-123"
        assert body["path_to_quarantine"] is False

@pytest.mark.asyncio
async def test_classify_document_quarantine_direct(mock_runner, mock_intel):
    synapse = MenirSynapse(mock_runner, mock_intel)
    
    # Mock JWT
    jwt_secret = "super_secret_menir_key_2026_replaced"
    os.environ["MENIR_JWT_SECRET"] = jwt_secret
    token = jwt.encode({"tenant_id": "BECO"}, jwt_secret, algorithm="HS256")
    
    # Mock Request
    mock_request = MagicMock(spec=web.Request)
    mock_request.headers = {"Authorization": f"Bearer {token}"}
    
    # Mock Multipart
    mock_field = AsyncMock()
    mock_field.name = 'file'
    mock_field.filename = 'bad.pdf'
    mock_field.read_chunk = AsyncMock(side_effect=[b"garbage", None])
    mock_multipart = AsyncMock()
    mock_multipart.next = AsyncMock(side_effect=[mock_field, None])
    mock_request.multipart = AsyncMock(return_value=mock_multipart)
    
    # Mock Low Confidence
    mock_classification = DocumentClassification(
        document_type="OTHER",
        suggested_client_name=None,
        confidence=0.4,
        language="en"
    )
    
    with patch("src.v3.core.synapse.DocumentClassifierSkill.classify_document", new_callable=AsyncMock) as mock_classify, \
         patch("src.v3.core.synapse.NodePersistenceOrchestrator.persist", new_callable=AsyncMock) as mock_persist:
        
        mock_classify.return_value = mock_classification
        mock_persist.return_value = "q-uid-456"
        
        response = await synapse.handle_classify_document(mock_request)
        
        assert response.status == 200
        body = json.loads(response.text)
        assert body["path_to_quarantine"] is True
        assert body["confidence"] == 0.4
