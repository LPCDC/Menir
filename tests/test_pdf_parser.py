import pytest
from unittest.mock import patch, MagicMock
from src.v3.core.pdf_parser import classify_pdf_type, PdfType

def test_classify_digital():
    # Mocking standard DIGITAL text
    with patch("src.v3.core.pdf_parser.PdfReader") as mock_reader:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is a clean, robust, simple normal digital PDF text without many newlines." * 10
        mock_reader.return_value.pages = [mock_page]
        
        pdf_type, content = classify_pdf_type("dummy.pdf")
        assert pdf_type == PdfType.DIGITAL
        assert "digital PDF text" in content[0]

def test_classify_scanned():
    # Mocking SCANNED (< 50 chars per page)
    with patch("src.v3.core.pdf_parser.PdfReader") as mock_reader, \
         patch("src.v3.core.pdf_parser.convert_to_scanned_parts") as mock_convert:
        
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "  short  " 
        mock_reader.return_value.pages = [mock_page]
        
        mock_convert.return_value = (PdfType.SCANNED, ["mock_image_data_1", "mock_image_data_2"])
        
        pdf_type, content = classify_pdf_type("dummy.pdf")
        assert pdf_type == PdfType.SCANNED
        assert content == ["mock_image_data_1", "mock_image_data_2"]

def test_classify_hybrid():
    # Mocking HYBRID (many newlines or high fragmentation ratio)
    with patch("src.v3.core.pdf_parser.PdfReader") as mock_reader:
        mock_page = MagicMock()
        # High newline ratio
        mock_page.extract_text.return_value = "a\nb\nc\nd\ne\n" * 20
        mock_reader.return_value.pages = [mock_page]
        
        pdf_type, content = classify_pdf_type("dummy.pdf")
        assert pdf_type == PdfType.HYBRID
        assert "INSTRUÇÃO DO CLASSIFICADOR HYBRID" in content[0]

def test_classify_hybrid_suspicious_chars():
    # Mocking HYBRID via suspicious characters > 5%
    with patch("src.v3.core.pdf_parser.PdfReader") as mock_reader:
        mock_page = MagicMock()
        # High suspicious chars ratio: using non-standard characters that are outside \w and basic punctuation
        mock_page.extract_text.return_value = "Normal text and then lots of garbage: " + ("\x01\x02\x03\x04\x7f\x80\x81\x82¶§" * 20)
        mock_reader.return_value.pages = [mock_page]
        
        pdf_type, content = classify_pdf_type("dummy.pdf")
        assert pdf_type == PdfType.HYBRID
        assert "INSTRUÇÃO DO CLASSIFICADOR HYBRID" in content[0]

def test_classify_scanned_fallback_on_exception():
    # Mocking SCANNED fallback when PdfReader throws an Exception
    with patch("src.v3.core.pdf_parser.PdfReader", side_effect=Exception("Corrupted PDF")), \
         patch("src.v3.core.pdf_parser.convert_to_scanned_parts") as mock_convert:
        
        mock_convert.return_value = (PdfType.SCANNED, ["fallback_image"])
        pdf_type, content = classify_pdf_type("corrupted.pdf")
        assert pdf_type == PdfType.SCANNED
        assert content == ["fallback_image"]
