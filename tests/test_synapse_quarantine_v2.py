import pytest
import json
import jwt
import os
from aiohttp import web
from unittest.mock import AsyncMock, MagicMock, patch
from src.v3.core.synapse import MenirSynapse

@pytest.fixture
def mock_runner():
    runner = MagicMock()
    runner.ontology_manager.driver.session = MagicMock()
    return runner

@pytest.fixture
def mock_intel():
    return MagicMock()

@pytest.mark.asyncio
async def test_get_quarantine_documents_with_trust_score(mock_runner, mock_intel):
    """
    Testa se o endpoint de quarentena retorna os campos trust_score e routing_decision.
    """
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
    # Simulando o que esperaremos no futuro
    mock_record.data.return_value = {
        "q": {
            "uid": "q-123",
            "name": "test.pdf",
            "document_type": "INVOICE_SUPPLIER",
            "suggested_client": "Ana Paula",
            "confidence": 0.65,
            "trust_score": 0.72,
            "routing_decision": "QUARANTINE",
            "language": "pt",
            "reason": "LOW_CONFIDENCE",
            "date": "2026-03-19T00:00:00Z"
        }
    }
    
    mock_result = MagicMock()
    mock_result.all.return_value = [mock_record]
    mock_session.run.return_value = mock_result
    
    response = await synapse.handle_get_quarantine_documents(mock_request)
    
    assert response.status == 200
    body = json.loads(response.text)
    assert len(body) == 1
    
    # Valida presença dos novos campos exigidos por Nicole
    assert "trust_score" in body[0]
    assert "routing_decision" in body[0]
    assert body[0]["trust_score"] == 0.72
    assert body[0]["routing_decision"] == "QUARANTINE"
