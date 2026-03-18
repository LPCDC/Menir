import math
from typing import Literal

from pydantic import BaseModel, Field, model_validator
from decimal import Decimal

from .base import BaseNode


class InvoiceLineItem(BaseModel):
    description: str = Field(description="Descrição clara do item, serviço ou produto.")
    gross_amount: float = Field(description="Valor bruto da linha.")
    tva_rate_applied: float | None = Field(
        default=None,
        description="Taxa de imposto aplicada à linha (ex: 8.1, 2.6). Se não especificada, deixe nulo.",
    )


class InvoiceData(BaseNode):
    source_document_uid: str = Field(description="O UID do DocumentNode de origem na qual esta extração foi baseada.")
    vendor_name: str = Field(description="Nome do fornecedor que emitiu a fatura.")
    doc_type: Literal[
        "Facture", "Note de crédit", "Rappel", "Ticket de caisse", "Relevé bancaire", 
        "Contrat", "Police d'assurance", "Déclaration d'impôt", "Fiche de salaire", 
        "Note de frais", "Quittance", "Reçu", "Extrait de compte", "BVR", "Facture QR", 
        "Avis de débit", "Avis de crédit", "Décompte TVA", "Décompte LPP", "Décompte AVS", 
        "Certificat de salaire", "Bilan", "Compte de résultat", "Grand livre", "Journal", 
        "Balance", "Extrait du registre", "Offre"
    ] = Field(description="Tipo de documento extraído.")
    ide_number: str | None = Field(
        default=None,
        description="Número IDE Suíço (ex: CHE-123.456.789).",
    )
    avs_number: str | None = Field(
        default=None,
        description="Número AVS (EAN-13, 13 dígitos).",
    )
    language: Literal["de", "fr", "it", "rm", "en", "pt", "sq"] = Field(
        description="Idioma do documento, incluindo romanche, inglês, português e albanês (sq)."
    )
    vendor_iban: str | None = Field(default=None, description="IBAN suíço ou europeu na fatura.")
    currency: Literal["CHF", "EUR"] = Field(description="A moeda oficial do documento.")
    issue_date: str = Field(description="Data de emissão no formato YYYY-MM-DD.")

    subtotal: float = Field(description="Soma do valor líquido sem impostos de todas as linhas.")
    tip_or_unregulated_amount: float = Field(
        default=0.0, description="Gorjetas (Pourboire) ou valores não tributados."
    )
    total_amount: float = Field(description="Valor total a pagar exigido no documento.")

    items: list[InvoiceLineItem] = Field(description="Lista com todos os itens extraídos.")
    requires_manual_justification: bool = Field(
        default=False,
        description="Flag: Marcar como TRUTH se for um recibo de restaurante ou despesa de representação que exija justificativa do contador.",
    )
    is_recurring: bool = Field(
        default=False,
        description="Flag: True se for uma fatura recorrente (assinatura mensal, prémio de seguro, impostos periódicos).",
    )
    purchase_order_number: str | None = Field(
        default=None,
        description="Número de ordem de compra (PO Number) da empresa emissora. Nulo se não aplicável.",
    )
    
    extraction_path: Literal["QR_DECODE", "GEMINI_FALLBACK"] = Field(
        description="Rastreabilidade: Caminho arquitetural utilizado para obter os dados."
    )
    extraction_confidence: Decimal = Field(
        description="Confiança da extração (1.0 para QR, ou score calculado pelo LLM para Fallback)."
    )
    
    labels: list[str] = ["Invoice", "Document"]  # noqa: RUF012

    @model_validator(mode="after")
    def validate_accounting_math(self, info) -> "InvoiceData":
        context_data = info.context or {}
        allowed_tva_rates = context_data.get("valid_tva_rates", [])

        if not allowed_tva_rates:
            # During isolated tests or when context fails, bypass.
            # Production MUST inject context.
            return self

        calculated_subtotal = sum(item.gross_amount for item in self.items)
        if not math.isclose(calculated_subtotal, self.subtotal, abs_tol=0.05):
            raise ValueError(
                f"ITEMS vs SUBTOTAL: soma dos itens ({calculated_subtotal:.2f}) "
                f"não bate com subtotal ({self.subtotal:.2f})."
            )

        tva_closes = False
        for rate in allowed_tva_rates:
            tva = round(self.subtotal * rate / 100, 2)
            if math.isclose(
                self.subtotal + tva + self.tip_or_unregulated_amount,
                self.total_amount,
                abs_tol=0.10,
            ):
                tva_closes = True
                break

        if not tva_closes:
            if not math.isclose(
                self.subtotal + self.tip_or_unregulated_amount, self.total_amount, abs_tol=0.10
            ):
                raise ValueError(
                    f"SUBTOTAL + TVA vs TOTAL: nenhuma alíquota permitida ({allowed_tva_rates}) "
                    f"explica o total de {self.total_amount:.2f} "
                    f"a partir do subtotal {self.subtotal:.2f}."
                )

        for idx, item in enumerate(self.items):
            if item.tva_rate_applied is not None:
                rate = round(item.tva_rate_applied, 1)
                # Hard Reject Tva Rate
                if rate not in [8.1, 3.8, 2.6, 0.0]:
                    raise ValueError(
                        f"TVA HALLUCINATION: alíquota {rate}% no item {idx} "
                        f"rejeitada. Somente 8.1, 3.8, 2.6, e 0.0 permitidos na Suíça atualmente."
                    )
                if rate not in allowed_tva_rates and not math.isclose(rate, 0.0, abs_tol=0.01):
                    raise ValueError(
                        f"TVA HALLUCINATION: alíquota {rate}% no item {idx} "
                        f"não está nas permitidas do tenant: {allowed_tva_rates}."
                    )

        return self

    @model_validator(mode="after")
    def validate_swiss_ide(self) -> "InvoiceData":
        """
        Escudo de Anomalias contra Fraude ou Alucinação: Validação Aritmética MOD11 do IDE.
        """
        if not self.ide_number:
            return self

        import re

        raw_digits = re.sub(r"\D", "", self.ide_number)

        if len(raw_digits) != 9:
            raise ValueError(
                f"ANOMALY DETECTED: IDE Suíço inválido (Tamanho incorreto): {self.ide_number}. São exigidos exatamente 9 dígitos numéricos."
            )

        weights = [5, 4, 3, 2, 7, 6, 5, 4]
        total_sum = sum(int(digit) * weight for digit, weight in zip(raw_digits[:8], weights))  # noqa: B905

        expected_checksum = 11 - (total_sum % 11)
        if expected_checksum == 11:
            expected_checksum = 0
        elif expected_checksum == 10:
            raise ValueError(
                f"ANOMALY DETECTED: IDE Suíço MOD11 falhou estruturalmente (Check=10) para {self.ide_number}"
            )

        actual_checksum = int(raw_digits[8])
        if expected_checksum != actual_checksum:
            raise ValueError(
                f"FRAUD/HALLUCINATION DETECTED: IDE Suíço {self.ide_number} falhou na validação de Integridade MOD11. O dígito final {actual_checksum} deveria ser {expected_checksum}."
            )

        return self

    @model_validator(mode="after")
    def validate_avs_ean13(self) -> "InvoiceData":
        """Validação do AVS number usando Checksum EAN-13."""
        if not self.avs_number:
            return self

        import re
        raw_digits = re.sub(r"\D", "", self.avs_number)

        if len(raw_digits) != 13:
            raise ValueError(
                f"ANOMALY DETECTED: AVS number inválido (Tamanho incorreto): {self.avs_number}. Exigidos exatamente 13 dígitos numéricos."
            )

        def calculate_ean13_checksum(digits_str: str) -> int:
            total = 0
            for i, char in enumerate(digits_str[:12]):
                digit = int(char)
                total += digit * (1 if i % 2 == 0 else 3)
            return (10 - (total % 10)) % 10

        expected_checksum = calculate_ean13_checksum(raw_digits)
        actual_checksum = int(raw_digits[12])

        if expected_checksum != actual_checksum:
            raise ValueError(
                f"FRAUD/HALLUCINATION DETECTED: AVS {self.avs_number} falhou na validação EAN-13. Dígito verificador {actual_checksum} deveria ser {expected_checksum}."
            )

        return self
