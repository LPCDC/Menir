"""
TDD: Testes de Roteamento (Fast Lane vs Quarentena) no DocumentClassifierSkill.
Fingerprint: MENIR-P46-20260318-PRE_TASK7_COMPLETE
Skill: pytest-engineer
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.v3.skills.document_classifier_skill import DocumentClassifierSkill, DocumentClassification


@pytest.fixture
def mock_intel():
    intel = MagicMock()
    intel.structured_inference = AsyncMock()
    return intel


@pytest.mark.asyncio
async def test_routing_fast_lane_high_confidence(mock_intel):
    """Documento com confiança > 0.85 deve ser marcado para PRODUCTION."""
    mock_intel.structured_inference.return_value = DocumentClassification(
        document_type="INVOICE_SUPPLIER",
        suggested_client_name="Vendor High",
        confidence=0.98,
        language="fr"
    )
    
    skill = DocumentClassifierSkill(mock_intel)
    
    with patch("src.v3.skills.document_classifier_skill.classify_pdf_type") as mock_parser:
        # Simula PDF Digital (que ganha bonus no engine)
        mock_parser.return_value = ("DIGITAL", ["Texto Frequente"])
        
        # O método classify_document deve retornar o destino agora
        classification, score, target = await skill.classify_document("high.pdf")
        
        assert target == "PRODUCTION"
        assert classification.confidence >= 0.85


@pytest.mark.asyncio
async def test_routing_quarantine_low_confidence(mock_intel):
    """Documento com confiança < 0.85 deve ser marcado para QUARANTINE."""
    mock_intel.structured_inference.return_value = DocumentClassification(
        document_type="INVOICE_SUPPLIER",
        suggested_client_name="Vendor Low",
        confidence=0.7,
        language="fr"
    )
    
    skill = DocumentClassifierSkill(mock_intel)
    
    with patch("src.v3.skills.document_classifier_skill.classify_pdf_type") as mock_parser:
        # Simula SCANNED (que perde pontos no engine se não tiver QR)
        mock_parser.return_value = ("SCANNED", ["Imagem ruidosa"])
        
        classification, score, target = await skill.classify_document("low.pdf")
        
        assert target == "QUARANTINE"
        assert classification.confidence < 0.85
