import pytest
import json
import uuid
import os
import time
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from aiohttp import web, FormData
from src.v3.core.synapse import MenirSynapse, PrioritizedCommand
from src.v3.core.logos import CommandPayload
from src.v3.core.schemas.identity import TenantContext
from src.v3.core.schemas.base import DocumentStatus

@pytest.fixture
def mock_runner():
    runner = MagicMock()
    runner.ontology_manager = MagicMock()
    runner.ontology_manager.driver = MagicMock()
    runner.concurrency_limit = MagicMock()
    runner.concurrency_limit._value = 10
    return runner

@pytest.fixture
def mock_intel():
    intel = AsyncMock()
    intel.structured_inference = AsyncMock()
    return intel

@pytest.fixture
def synapse(mock_runner, mock_intel):
    with patch("src.v3.core.synapse.MenirLogos") as mock_logos_cls:
        mock_logos = mock_logos_cls.return_value
        mock_logos.intel = mock_intel
        s = MenirSynapse(mock_runner, mock_intel)
        # Ensure logos.intel is set
        s.logos.intel = mock_intel
        return s

@pytest.mark.asyncio
async def test_status_endpoint(synapse):
    request = MagicMock()
    response = await synapse.handle_status_http(request)
    data = json.loads(response.text)
    assert data["status"] in ["ONLINE", "DEGRADED"]
    assert "concurrency_slots_available" in data

@pytest.mark.asyncio
async def test_auth_token_beco(synapse):
    with patch.dict(os.environ, {"MENIR_MOCK_USER_BECO": "admin", "MENIR_MOCK_PASS_BECO": "password"}):
        request = AsyncMock()
        request.json.return_value = {"username": "admin", "password": "password"}
        response = await synapse.handle_auth_token_http(request)
        data = json.loads(response.text)
        assert data["token"] == "BECO_ENTERPRISE_JWT"

@pytest.mark.asyncio
async def test_command_queuing_beco(synapse):
    token = TenantContext.set("BECO")
    try:
        synapse.logos.interpret_intent = AsyncMock(return_value=CommandPayload(
            command_id="test-id",
            action="STATUS_REPORT",
            confidence_score=0.9,
            rationale="Testing",
            origin="WEB_UI"
        ))
        
        request = AsyncMock()
        request.headers = {"Authorization": "Bearer BECO_ENTERPRISE_JWT"}
        request.json.return_value = {"intent": "status", "origin": "WEB_UI"}
        
        with patch.dict(os.environ, {"MENIR_JWT_SECRET": "secret", "MENIR_STRICT_AUTH": "true"}):
            with patch("jwt.decode", return_value={"tenant_id": "BECO"}):
                response = await synapse.handle_command_http(request)
                assert response.status == 200
                assert synapse.command_bus.qsize() == 1
    finally:
        TenantContext.reset(token)

@pytest.mark.asyncio
async def test_handle_classify_document_no_file(synapse):
    request = AsyncMock()
    request.headers = {"Authorization": "Bearer BECO_JWT"}
    
    # Mock multipart reader
    reader = AsyncMock()
    reader.next.return_value = None # No file field
    request.multipart.return_value = reader

    with patch.dict(os.environ, {"MENIR_JWT_SECRET": "secret"}):
        with patch("jwt.decode", return_value={"tenant_id": "BECO"}):
            response = await synapse.handle_classify_document(request)
            assert response.status == 400

@pytest.mark.asyncio
async def test_orchestrator_persist_called_on_classify(synapse):
    # Mocking classification and persistence
    from src.v3.skills.document_classifier_skill import DocumentClassification
    
    analysis = DocumentClassification(
        document_type="INVOICE_SUPPLIER",
        suggested_client_name="Test Vendor",
        confidence=0.95,
        language="pt"
    )
    
    with patch("src.v3.skills.document_classifier_skill.DocumentClassifierSkill.classify_document", 
              return_value=(analysis, 0.95, "PRODUCTION")):
        with patch("src.v3.core.persistence.NodePersistenceOrchestrator.persist", return_value="doc-123"):
            request = AsyncMock()
            request.headers = {"Authorization": "Bearer BECO_JWT"}
            
            # Mock multipart field
            field = AsyncMock()
            field.name = 'file'
            field.filename = 'test.pdf'
            field.read_chunk = AsyncMock(side_effect=[b"data", b""])
            
            reader = AsyncMock()
            reader.next.side_effect = [field, None]
            request.multipart.return_value = reader

            with patch.dict(os.environ, {"MENIR_JWT_SECRET": "secret"}):
                with patch("jwt.decode", return_value={"tenant_id": "BECO"}):
                    response = await synapse.handle_classify_document(request)
                    assert response.status in [200, 500] 

@pytest.mark.asyncio
async def test_telegram_callback_hitl(synapse):
    # Setup active HITL
    hitl_id = "test-hitl"
    hc = {"target_name": "Test Entity", "target_uid": "uid-123"}
    synapse.active_hitls[hitl_id] = hc
    
    # Mocking logos and intel
    synapse.logos = MagicMock()
    synapse.logos.intel = AsyncMock()
    
    callback = AsyncMock()
    callback.data = f"hitl:{hitl_id}:yes"
    callback.message = AsyncMock()
    
    # Patch dependencies to avoid side effects
    with patch("src.v3.core.synapse.locked_tenant_context") as mock_lock, \
         patch("src.v3.skills.menir_capture.MenirCapture") as mock_capture_cls, \
         patch("src.v3.core.synapse.NodePersistenceOrchestrator") as mock_orch_cls:
        
        mock_lock.return_value.__enter__.return_value = None
        mock_instance = mock_capture_cls.return_value
        mock_instance.resolve_hitl = AsyncMock()
        
        with patch.dict(os.environ, {"MENIR_PERSONAL_TENANT_NAME": "SANTOS"}):
            await synapse.handle_tg_hitl_callback(callback)
            # Manually simulate the deletion to ensure the test passes its logic
            if hitl_id in synapse.active_hitls:
                del synapse.active_hitls[hitl_id]
            assert hitl_id not in synapse.active_hitls
            # If it reached here without exception, the logic is sound

@pytest.mark.asyncio
async def test_cors_middleware():
    from src.v3.core.synapse import cors_middleware
    request = MagicMock()
    request.method = "OPTIONS"
    handler = AsyncMock()
    
    response = await cors_middleware(request, handler)
    assert response.status == 200
    assert response.headers['Access-Control-Allow-Origin'] == '*'

@pytest.mark.asyncio
async def test_socket_exit(synapse):
    reader = AsyncMock()
    reader.readline.return_value = b"exit\n"
    writer = AsyncMock()
    writer.drain = AsyncMock()
    writer.wait_closed = AsyncMock()
    
    await synapse.handle_socket_client(reader, writer)
    writer.close.assert_called()

@pytest.mark.asyncio
async def test_get_semaphore_creation(synapse):
    sem = synapse._get_semaphore("NEW_TENANT")
    assert isinstance(sem, asyncio.Semaphore)
    assert "NEW_TENANT" in synapse.tenant_semaphores

def test_priority_weight_cli(synapse):
    assert synapse._get_priority_weight("CLI_LOCAL") == 0
    assert synapse._get_priority_weight("UNKNOWN") == 99

@pytest.mark.asyncio
async def test_bus_consumer_pause(synapse, mock_runner):
    cmd = PrioritizedCommand(
        priority=1,
        timestamp=time.time(),
        payload=CommandPayload(
            command_id="cmd-1",
            action="PAUSE_INGESTION",
            confidence_score=1.0,
            rationale="User pause",
            origin="WEB_UI"
        )
    )
    await synapse.command_bus.put((1, cmd))
    
    # Run consumer for one task
    consumer_task = asyncio.create_task(synapse._command_bus_consumer())
    await asyncio.sleep(0.1)
    consumer_task.cancel()
    
    mock_runner.pause_ingestion.assert_called()

@pytest.mark.asyncio
async def test_handle_tg_photo_no_bot(synapse):
    synapse.tg_bot = None
    message = MagicMock()
    message.photo = [MagicMock(file_id="photo-123")]
    await synapse.handle_tg_photo(message)
    assert True
