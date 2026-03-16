import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.v3.skills.document_classifier_skill import DocumentClassifierSkill, DocumentClassification

@pytest.fixture
def mock_intel():
    intel = MagicMock()
    intel.structured_inference = AsyncMock()
    return intel

@pytest.mark.asyncio
async def test_classify_invoice_portuguese(mock_intel):
    mock_intel.structured_inference.return_value = DocumentClassification(
        document_type="INVOICE",
        suggested_client_name="Ana Paula",
        confidence=0.98,
        language="pt"
    )
    
    skill = DocumentClassifierSkill(mock_intel)
    
    with patch("src.v3.skills.document_classifier_skill.classify_pdf_type") as mock_parser:
        mock_parser.return_value = ("DIGITAL", ["Texto de fatura em português"])
        
        result = await skill.classify_document("dummy.pdf")
        
        assert result.document_type == "INVOICE"
        assert result.language == "pt"
        assert result.confidence > 0.7
        assert result.suggested_client_name == "Ana Paula"

@pytest.mark.asyncio
async def test_classify_bank_statement_french(mock_intel):
    mock_intel.structured_inference.return_value = DocumentClassification(
        document_type="BANK_STATEMENT",
        suggested_client_name=None,
        confidence=0.99,
        language="fr"
    )
    
    skill = DocumentClassifierSkill(mock_intel)
    
    with patch("src.v3.skills.document_classifier_skill.classify_pdf_type") as mock_parser:
        mock_parser.return_value = ("DIGITAL", ["Extrait de compte bancaire en français"])
        
        result = await skill.classify_document("bank.pdf")
        
        assert result.document_type == "BANK_STATEMENT"
        assert result.language == "fr"
        assert result.confidence > 0.7

@pytest.mark.asyncio
async def test_classify_ambiguous_low_confidence(mock_intel):
    mock_intel.structured_inference.return_value = DocumentClassification(
        document_type="LETTER",
        suggested_client_name=None,
        confidence=0.45,
        language="en"
    )
    
    skill = DocumentClassifierSkill(mock_intel)
    
    with patch("src.v3.skills.document_classifier_skill.classify_pdf_type") as mock_parser:
        mock_parser.return_value = ("DIGITAL", ["Random English letter without context"])
        
        result = await skill.classify_document("ambiguous.pdf")
        
        assert result.document_type == "LETTER"
        assert result.confidence < 0.7
        assert result.language == "en"

@pytest.mark.asyncio
async def test_classify_error_fallback(mock_intel):
    mock_intel.structured_inference.side_effect = Exception("API Error")
    
    skill = DocumentClassifierSkill(mock_intel)
    
    with patch("src.v3.skills.document_classifier_skill.classify_pdf_type") as mock_parser:
        mock_parser.return_value = ("DIGITAL", ["..."])
        
        result = await skill.classify_document("error.pdf")
        
        assert result.document_type == "OTHER"
        assert result.confidence == 0.0
        assert result.language == "??"
