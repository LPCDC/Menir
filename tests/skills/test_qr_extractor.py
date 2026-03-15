import pytest
import os
from src.v3.skills.qr_extractor import extract_qr_from_pdf

@pytest.mark.asyncio
async def test_extract_qr_returns_data_for_valid_pdf():
    pdf_path = "tests/fixtures/style-guide-qr-bill-en.pdf"
    
    # Run the extractor
    result = await extract_qr_from_pdf(pdf_path)
    
    assert result is not None
    assert result["account"] == "CH3600000000000000000"
    assert "amount" in result

@pytest.mark.asyncio
async def test_extract_qr_returns_none_for_missing_file():
    pdf_path = "tests/fixtures/does_not_exist_at_all.pdf"
    result = await extract_qr_from_pdf(pdf_path)
    assert result is None

@pytest.mark.asyncio
async def test_extract_qr_returns_none_for_pdf_without_qr(tmp_path):
    # We create a dummy empty pdf here (tests/fixtures might not have a clean one ready, so we build it)
    from reportlab.pdfgen import canvas
    pdf_path = os.path.join(tmp_path, "empty.pdf")
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 800, "I have no QR code")
    c.save()
    
    result = await extract_qr_from_pdf(pdf_path)
    assert result is None
