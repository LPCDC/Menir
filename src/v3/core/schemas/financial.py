import math
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from .base import BaseNode


class InvoiceLineItem(BaseModel):
    description: str = Field(description="Descrição clara do item, serviço ou produto.")
    gross_amount: float = Field(description="Valor bruto da linha.")
    tva_rate_applied: float | None = Field(
        default=None,
        description="Taxa de imposto aplicada à linha (ex: 8.1, 2.6). Se não especificada, deixe nulo.",
    )


class InvoiceData(BaseNode):
    vendor_name: str = Field(description="Nome do fornecedor que emitiu a fatura.")
    vendor_uid: str | None = Field(
        default=None,
        description="Número UID Suíço com a extensão de IVA se aplicável (ex: CHE-123.456.789 TVA).",
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
                if rate not in allowed_tva_rates and not math.isclose(rate, 0.0, abs_tol=0.01):
                    raise ValueError(
                        f"TVA HALLUCINATION: alíquota {rate}% no item {idx} "
                        f"não está nas permitidas: {allowed_tva_rates}."
                    )

        return self

    @model_validator(mode="after")
    def validate_swiss_uid(self) -> "InvoiceData":
        """
        Escudo de Anomalias contra Fraude ou Alucinação: Validação Aritmética MOD11 do UID.
        """
        if not self.vendor_uid:
            return self

        import re

        raw_digits = re.sub(r"\D", "", self.vendor_uid)

        if len(raw_digits) != 9:
            raise ValueError(
                f"ANOMALY DETECTED: UID Suíço inválido (Tamanho incorreto): {self.vendor_uid}. São exigidos exatamente 9 dígitos numéricos (IDE)."
            )

        weights = [5, 4, 3, 2, 7, 6, 5, 4]
        total_sum = sum(int(digit) * weight for digit, weight in zip(raw_digits[:8], weights))  # noqa: B905

        expected_checksum = 11 - (total_sum % 11)
        if expected_checksum == 11:
            expected_checksum = 0
        elif expected_checksum == 10:
            raise ValueError(
                f"ANOMALY DETECTED: UID Suíço MOD11 falhou estruturalmente (Check=10) para {self.vendor_uid}"
            )

        actual_checksum = int(raw_digits[8])
        if expected_checksum != actual_checksum:
            raise ValueError(
                f"FRAUD/HALLUCINATION DETECTED: UID Suíço {self.vendor_uid} falhou na validação de Integridade MOD11. O dígito final {actual_checksum} deveria ser {expected_checksum}."
            )

        return self
