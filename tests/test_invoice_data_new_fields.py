"""
TDD — Ajuste 2: is_recurring e purchase_order_number em InvoiceData.
Fingerprint: MENIR-P46-20260318-PRE_TASK7_COMPLETE
Padrão: Red → Green → Refactor (tdd-python skill)
"""
import pytest
from decimal import Decimal
from src.v3.core.schemas.financial import InvoiceData, InvoiceLineItem


def _base_invoice(**overrides) -> dict:
    """Factory de InvoiceData válido para reutilização nos testes."""
    base = {
        "uid": "test-uid-001",
        "project": "BECO",
        "source_document_uid": "doc-uid-001",
        "vendor_name": "Test Vendor SA",
        "doc_type": "Facture QR",
        "language": "fr",
        "currency": "CHF",
        "issue_date": "2024-09-01",
        "subtotal": 100.0,
        "tip_or_unregulated_amount": 0.0,
        "total_amount": 100.0,
        "items": [InvoiceLineItem(description="Service", gross_amount=100.0)],
        "extraction_path": "QR_DECODE",
        "extraction_confidence": Decimal("1.0"),
    }
    base.update(overrides)
    return base


class TestInvoiceDataNewFields:
    """Testa os dois novos campos: is_recurring e purchase_order_number."""

    def test_default_values_both_fields_absent(self):
        """Fatura padrão sem os novos campos deve usar defaults."""
        # Arrange & Act
        invoice = InvoiceData(**_base_invoice())
        # Assert
        assert invoice.is_recurring is False
        assert invoice.purchase_order_number is None

    def test_sbb_fatura_com_purchase_order_number(self):
        """Fatura SBB com número de ordem de compra deve persistir o valor."""
        # Arrange
        data = _base_invoice(
            vendor_name="SBB CFF FFS",
            purchase_order_number="PO-2024-SBB-00123",
        )
        # Act
        invoice = InvoiceData(**data)
        # Assert
        assert invoice.purchase_order_number == "PO-2024-SBB-00123"
        assert invoice.is_recurring is False  # default não afetado

    def test_aci_vaud_fatura_recorrente(self):
        """Avis de taxation da ACI Vaud marcado como recorrente."""
        # Arrange
        data = _base_invoice(
            vendor_name="Administration Cantonale des Impôts VD",
            doc_type="Déclaration d'impôt",
            is_recurring=True,
        )
        # Act
        invoice = InvoiceData(**data)
        # Assert
        assert invoice.is_recurring is True
        assert invoice.purchase_order_number is None  # default não afetado

    def test_both_fields_set_simultaneously(self):
        """Ambos os campos podem ser definidos juntos sem conflito."""
        # Arrange
        data = _base_invoice(
            is_recurring=True,
            purchase_order_number="PO-BECO-2024-009",
        )
        # Act
        invoice = InvoiceData(**data)
        # Assert
        assert invoice.is_recurring is True
        assert invoice.purchase_order_number == "PO-BECO-2024-009"

    def test_is_recurring_false_explicit(self):
        """is_recurring=False explícito deve ser aceito sem erro."""
        # Arrange
        data = _base_invoice(is_recurring=False)
        # Act
        invoice = InvoiceData(**data)
        # Assert
        assert invoice.is_recurring is False

    def test_purchase_order_number_none_explicit(self):
        """purchase_order_number=None explícito deve ser aceito."""
        # Arrange
        data = _base_invoice(purchase_order_number=None)
        # Act
        invoice = InvoiceData(**data)
        # Assert
        assert invoice.purchase_order_number is None
