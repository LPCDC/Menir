import pytest
import os
import os.path
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
async def test_export_cresus_no_content(mock_runner, mock_intel):
    synapse = MenirSynapse(mock_runner, mock_intel)
    
    mock_request = MagicMock(spec=web.Request)
    mock_request.headers = {}
    
    with patch("src.v3.core.cresus_exporter.CresusExporter.export_reconciled", new_callable=AsyncMock) as mock_export:
        mock_export.return_value = None # No document found
        
        response = await synapse.handle_export_cresus(mock_request)
        
        assert response.status == 204
        assert response.body is None

@pytest.mark.asyncio
async def test_export_cresus_success(mock_runner, mock_intel):
    synapse = MenirSynapse(mock_runner, mock_intel)
    
    mock_request = MagicMock(spec=web.Request)
    mock_request.headers = {}
    
    with patch("src.v3.core.cresus_exporter.CresusExporter.export_reconciled", new_callable=AsyncMock) as mock_export:
        mock_export.return_value = "/path/to/export.csv"
        
        response = await synapse.handle_export_cresus(mock_request)
        
        assert response.status == 200
        import json
        body = json.loads(response.text)
        assert body["success"] is True
        assert body["file_path"] == "/path/to/export.csv"
