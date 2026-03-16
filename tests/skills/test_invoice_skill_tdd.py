import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal

from src.v3.skills.invoice_skill import InvoiceSkill
from src.v3.core.schemas.identity import TenantContext

@pytest.fixture
def mock_intel():
    intel = MagicMock()
    intel.structured_inference = AsyncMock()
    return intel

@pytest.fixture
def mock_ontology_manager():
    manager = MagicMock()
    manager.get_tenant_active_context.return_value = {"tva_rates": [8.1, 2.6, 0.0]}
    
    # Mock driver and session for transaction 
    session_mock = MagicMock()
    tx_mock = MagicMock()
    session_mock.__enter__.return_value = session_mock
    session_mock.begin_transaction.return_value.__enter__.return_value = tx_mock
    manager.driver.session.return_value = session_mock
    
    return manager

@pytest.fixture
def invoice_skill(mock_intel, mock_ontology_manager):
    return InvoiceSkill(intel=mock_intel, ontology_manager=mock_ontology_manager)

@pytest.mark.asyncio
@patch('src.v3.skills.qr_extractor.extract_qr_from_pdf')
@patch('os.getenv')
async def test_path_a_qr_decode(mock_getenv, mock_extract, invoice_skill, monkeypatch):
    """
    Test Path A: Se o QR extractor retornar dados, usa direct extraction.
    extraction_path == 'QR_DECODE', extraction_confidence == 1.0.
    """
    mock_getenv.return_value = "true" # MENIR_INVOICE_LIVE=true
    TenantContext.set("BECO")
    
    qr_data = {
        "account": "CH3600000000000000000",
        "creditor": {"name": "QR Fornecedor"},
        "amount": 100.50,
        "currency": "CHF",
        "unstructured_message": "Fatura QR"
    }
    
    mock_extract.return_value = qr_data
    invoice_skill._resolve_vendor_zefix = AsyncMock(return_value=(True, "MATCH"))
    
    # Mock Orchestrator to capture what is being persisted
    persisted_node = None
    async def mock_persist(node, tx):
        nonlocal persisted_node
        persisted_node = node
        return node.uid
        
    with patch('src.v3.core.persistence.NodePersistenceOrchestrator') as mock_orchestrator_class:
        mock_instance = mock_orchestrator_class.return_value
        mock_instance.persist = mock_persist
        
        result = await invoice_skill.process_document("tests/fixtures/invoice_beco_sanitized.pdf")
        print(f"DEBUG RESULT A: {result.message}")
        
        assert result.success is True
        assert persisted_node is not None
        assert persisted_node.extraction_path == "QR_DECODE"
        assert persisted_node.extraction_confidence == Decimal("1.0")
        
        # Gemini never called
        invoice_skill.intel.structured_inference.assert_not_called()


@pytest.mark.asyncio
@patch('src.v3.skills.qr_extractor.extract_qr_from_pdf')
@patch('os.getenv')
async def test_path_b_gemini_fallback(mock_getenv, mock_extract, invoice_skill):
    """
    Test Path B: Se QR Extractor retornar None, fallback pro Gemini AI.
    extraction_path == 'GEMINI_FALLBACK', extraction_confidence pelo LLM.
    """
    mock_getenv.return_value = "true" # MENIR_INVOICE_LIVE=true
    TenantContext.set("BECO")
    
    mock_extract.return_value = None
    invoice_skill._resolve_vendor_zefix = AsyncMock(return_value=(True, "MATCH"))
    
    gemini_data = {
        "vendor_name": "Google",
        "doc_type": "Facture",
        "ide_number": None,
        "avs_number": None,
        "language": "en",
        "vendor_iban": None,
        "currency": "CHF",
        "issue_date": "2025-10-10",
        "subtotal": 200.0,
        "tip_or_unregulated_amount": 0.0,
        "total_amount": 200.0,
        "items": [{"description": "Ads", "gross_amount": 200.0, "tva_rate_applied": 0.0}],
        "requires_manual_justification": False,
        "extraction_confidence": 0.95
    }
    
    invoice_skill.intel.structured_inference.return_value = gemini_data
    
    # Mock Orchestrator
    persisted_node = None
    async def mock_persist(node, tx):
        nonlocal persisted_node
        persisted_node = node
        return node.uid
        
    with patch('src.v3.core.persistence.NodePersistenceOrchestrator') as mock_orchestrator:
        mock_instance = mock_orchestrator.return_value
        mock_instance.persist = mock_persist
        
        result = await invoice_skill.process_document("tests/fixtures/invoice_beco_sanitized.pdf")
        print(f"DEBUG RESULT B: {result.message}")
        
        assert result.success is True
        assert persisted_node.extraction_path == "GEMINI_FALLBACK"
        assert persisted_node.extraction_confidence == Decimal("0.95")
        
        # Gemini was called
        invoice_skill.intel.structured_inference.assert_called_once()
