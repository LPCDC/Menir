import pytest
from pydantic import ValidationError
from src.v3.skills.sanitize_clients import ClientInput, ClientType

def test_valid_client_minimum():
    data = {
        "name": "Ana Paula",
        "client_type": "INDIVIDUAL",
        "canton": "VD",
        "language": "fr"
    }
    client = ClientInput(**data)
    assert client.name == "Ana Paula"
    assert client.client_type == ClientType.INDIVIDUAL
    assert client.fiscal_id is None

def test_valid_client_with_fiscal_id(monkeypatch):
    # Mock validate_mod11 to return True
    import src.v3.skills.swiss_qr_parser as sqp
    monkeypatch.setattr(sqp.SwissQRParser, "validate_mod11", lambda self, x, raise_error=False: True)
    
    data = {
        "name": "Entreprise SA",
        "client_type": "COMPANY",
        "canton": "GE",
        "language": "en",
        "fiscal_id": "CHE-123.456.789"
    }
    client = ClientInput(**data)
    assert client.fiscal_id == "CHE123456789" # Formatação removida

def test_invalid_client_type():
    data = {
        "name": "Empresa",
        "client_type": "INVALID_TYPE",
        "canton": "GE",
        "language": "en"
    }
    with pytest.raises(ValidationError):
        ClientInput(**data)

def test_invalid_fiscal_id(monkeypatch):
    import src.v3.skills.swiss_qr_parser as sqp
    monkeypatch.setattr(sqp.SwissQRParser, "validate_mod11", lambda self, x, raise_error=False: False)
    
    data = {
        "name": "Empresa Falsa",
        "client_type": "COMPANY",
        "canton": "GE",
        "language": "fr",
        "fiscal_id": "CHE-000.000.000"
    }
    with pytest.raises(ValidationError) as exc:
        ClientInput(**data)
    assert "Falha na validaca MOD97-10 do fiscal_id" in str(exc.value)

def test_forbid_extra_fields():
    data = {
        "name": "Ana Paula",
        "client_type": "INDIVIDUAL",
        "canton": "VD",
        "language": "fr",
        "extra_field": "not allowed"
    }
    with pytest.raises(ValidationError):
        ClientInput(**data)
