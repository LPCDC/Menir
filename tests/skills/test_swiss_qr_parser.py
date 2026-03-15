import pytest
from decimal import Decimal
from src.v3.skills.swiss_qr_parser import SwissQRParser, SwissQRParserError

# Real QR-IBAN from Swiss Style Guide (valid mod 97)
VALID_QR_IBAN = "CH3600000000000000000"
INVALID_QR_IBAN = "CH3600000000000000001"

# A valid Style Guide payload (Type S structured addresses)
# Contains 34 lines as per SIX v2.3 standard.
VALID_QRR_PAYLOAD = (
    "SPC\n"           # 1. QRType
    "0201\n"          # 2. Version
    "1\n"             # 3. Coding
    f"{VALID_QR_IBAN}\n" # 4. Account (QR-IBAN here)
    "S\n"             # 5. Creditor Address Type (Structured)
    "Creditor Name\n" # 6. Name
    "Musterstrasse\n" # 7. Street
    "15\n"            # 8. Building number
    "1000\n"          # 9. Postal code
    "Lausanne\n"      # 10. Town
    "CH\n"            # 11. Country
    "\n"              # 12. Ultimate Creditor Addr Type (Optional)
    "\n"              # 13. Name
    "\n"              # 14. Street
    "\n"              # 15. Bldg number
    "\n"              # 16. Postal Code
    "\n"              # 17. Town
    "\n"              # 18. Country
    "100.50\n"        # 19. Amount
    "CHF\n"           # 20. Currency
    "S\n"             # 21. Ultimate Debtor Addr Type (Structured)
    "Debtor Name\n"   # 22. Name
    "Debtor Street\n" # 23. Street
    "2\n"             # 24. Bldg number
    "2000\n"          # 25. Postal code
    "Neuchatel\n"     # 26. Town
    "CH\n"            # 27. Country
    "QRR\n"           # 28. Ref Type
    "123456789012345678901234567\n" # 29. Reference
    "Invoice #123\n"  # 30. Unstructured msg
    "EPD\n"           # 31. Trailer
    "Billing Info\n"  # 32. Billing Info
    "\n"              # 33. Alt Scheme 1
    "\n"              # 34. Alt Scheme 2
)

INVALID_ADDRESS_TYPE_PAYLOAD = VALID_QRR_PAYLOAD.replace("S\nCreditor Name", "K\nCreditor Name")

def test_parse_valid_qrr_payload():
    parser = SwissQRParser()
    result = parser.parse(VALID_QRR_PAYLOAD)
    
    assert result["account"] == VALID_QR_IBAN
    assert result["creditor"]["name"] == "Creditor Name"
    assert result["creditor"]["address_type"] == "S"
    assert result["creditor"]["street"] == "Musterstrasse"
    assert result["creditor"]["building_number"] == "15"
    assert result["creditor"]["postal_code"] == "1000"
    assert result["creditor"]["town"] == "Lausanne"
    assert result["creditor"]["country"] == "CH"
    
    assert result["amount"] == Decimal("100.50")
    assert result["currency"] == "CHF"
    
    assert result["reference_type"] == "QRR"
    assert result["reference"] == "123456789012345678901234567"
    assert result["unstructured_message"] == "Invoice #123"

def test_parse_invalid_address_type_rejects_type_k():
    parser = SwissQRParser()
    with pytest.raises(SwissQRParserError) as exc:
        parser.parse(INVALID_ADDRESS_TYPE_PAYLOAD)
    assert "Somente enderecos estruturados (Type S) sao aceitos" in str(exc.value)

def test_parse_detects_scor():
    payload = VALID_QRR_PAYLOAD.replace("QRR\n123456789012345678901234567\n", "SCOR\nRF18539007547034\n")
    parser = SwissQRParser()
    result = parser.parse(payload)
    assert result["reference_type"] == "SCOR"
    assert result["reference"] == "RF18539007547034"

def test_parse_detects_non():
    payload = VALID_QRR_PAYLOAD.replace("QRR\n123456789012345678901234567\n", "NON\n\n")
    parser = SwissQRParser()
    result = parser.parse(payload)
    assert result["reference_type"] == "NON"
    assert result["reference"] == ""

def test_mod11_validation():
    # As explicitly requested: "Deve validar QR-IBAN com MOD11" ISO 7064
    parser = SwissQRParser()
    
    # Real valid ISO 7064 QR-IBAN
    assert parser.validate_mod11(VALID_QR_IBAN) == True
    
    # Simulating a failure for a corrupted IBAN
    with pytest.raises(SwissQRParserError) as exc:
        parser.validate_mod11(INVALID_QR_IBAN, raise_error=True)
    assert "Falha na validacao MOD11 (ISO 7064)" in str(exc.value)

def test_parse_invalid_iban_rejects_payload():
    parser = SwissQRParser()
    invalid_payload = VALID_QRR_PAYLOAD.replace(VALID_QR_IBAN, INVALID_QR_IBAN)
    
    with pytest.raises(SwissQRParserError) as exc:
        parser.parse(invalid_payload)
    assert "Falha na validacao MOD11" in str(exc.value)
