import pytest
from pydantic import ValidationError

# Import the new centralized schemas
from src.v3.core.schemas.financial import InvoiceData
from src.v3.core.schemas.identity import ALLOWED_TENANTS, Tenant


def test_tenant_isolation_strict():
    """
    Mock Test B: Verify Tenant isolation (BECO vs. SANTOS) at the Pydantic level.
    """
    # 1. Valid Tenants must construct successfully
    t1 = Tenant(uid="1", project="BECO", name="BECO")
    t2 = Tenant(uid="2", project="SANTOS", name="SANTOS")
    assert t1.name in ALLOWED_TENANTS
    assert t2.name in ALLOWED_TENANTS

    # 2. Invalid Tenant must raise a ValidationError before Neo4j is even touched
    with pytest.raises(ValidationError) as exc_info:
        Tenant(uid="3", project="UNKNOWN", name="UNKNOWN_TENANT")

    # Specific assert to ensure it's failing on the constraint
    assert "Input should be 'BECO' or 'SANTOS'" in str(exc_info.value)


def test_financial_schema_legacy_migration_with_mod11():
    """
    Mock Test A: Validate legacy InvoiceData falls to the new constraints.
    If the MOD11 Checksum of a vendor_uid is invalid, the strict=True (or default Pydantic V2)
    validation must reject it outright.
    """
    # Legacy data dictionary structure
    legacy_invoice_dict = {
        "uid": "inv_001",
        "project": "BECO",  # tenant_id in BaseNode
        "vendor_name": "Test Vendor AG",
        # INVALID MOD11 UID: The checksum will fail
        "vendor_uid": "CHE-111.111.111 TVA",
        "currency": "CHF",
        "issue_date": "2024-01-01",
        "subtotal": 100.0,
        "tip_or_unregulated_amount": 0.0,
        "total_amount": 108.1,
        "items": [
            {"description": "Consulting Services", "gross_amount": 100.0, "tva_rate_applied": 8.1}
        ],
    }

    # Should raise ValidationError due to MOD11 Validation failure
    with pytest.raises(ValidationError) as exc_info:
        # Pydantic V2 model_validate used by OGM
        InvoiceData.model_validate(legacy_invoice_dict)

    # Check that error is specifically the MOD11 anomaly shield
    assert "MOD11 falhou" in str(
        exc_info.value
    ) or "falhou na validação de Integridade MOD11" in str(exc_info.value)


def test_financial_schema_legacy_migration_valid_mod11():
    """
    Mock Test A.1: Validate legacy InvoiceData passes if MOD11 is structurally sound.
    """
    # A valid Swiss UID for test purposes: CHE-114.281.258
    # raw_digits: 11428125, checksum: 8
    # 1*5 + 1*4 + 4*3 + 2*2 + 8*7 + 1*6 + 2*5 + 5*4
    # 5 + 4 + 12 + 4 + 56 + 6 + 10 + 20 = 117
    # 117 % 11 = 7. 11 - 7 = 4... Wait. Let's find a valid one mathematically.
    # We will use "CHE-109.322.551" -> IDE: 10932255 1
    # 1*5 + 0 + 9*3 + 3*2 + 2*7 + 2*6 + 5*5 + 5*4 = 5 + 0 + 27 + 6 + 14 + 12 + 25 + 20 = 109
    # 109 % 11 = 10. 11 - 10 = 1. -> Matches final digit 1.

    legacy_invoice_dict_valid = {
        "uid": "inv_002",
        "project": "BECO",
        "vendor_name": "Valora AG",
        "vendor_uid": "CHE-109.322.551",
        "currency": "CHF",
        "issue_date": "2024-01-01",
        "subtotal": 100.0,
        "total_amount": 108.1,
        "items": [{"description": "Items", "gross_amount": 100.0, "tva_rate_applied": 8.1}],
    }

    # Should pass without throwing ValidationError
    # Note: We must inject the context for TVA validation to pass!
    invoice = InvoiceData.model_validate(
        legacy_invoice_dict_valid, context={"valid_tva_rates": [8.1, 2.6, 2.5]}
    )

    assert invoice.vendor_uid == "CHE-109.322.551"
    assert invoice.total_amount == 108.1
