from pydantic import Field
from src.v3.core.schemas.base import BaseNode

class ClientNode(BaseNode):
    """Nó raiz representando um cliente PF/PJ da BECO."""
    source_document_uid: str
    client_type: str = Field(description="PF (Natural Person) or PJ (Legal Entity)")
    name: str
    ide_number: str | None = None
    address: str | None = None

class EmployeeNode(BaseNode):
    """Trabalhador vinculado a um cliente PJ da BECO."""
    source_document_uid: str
    full_name: str
    avs_number: str | None = None
    role: str | None = None
    hiring_date: str | None = None

class TaxDossierNode(BaseNode):
    """Exercício fiscal agregado de um cliente."""
    source_document_uid: str
    year: int
    tax_authority: str | None = None
    status: str | None = None

class InsuranceNode(BaseNode):
    """Apólice ou contrato de seguro (LPP/AVS) vinculado a cliente/funcionário."""
    source_document_uid: str
    policy_number: str
    provider_name: str
    insurance_type: str = Field(description="LPP, AVS, RC, etc.")

class SalarySlipNode(BaseNode):
    """Ficha do mês (Fiche de Salaire) extraída do software de Payroll."""
    source_document_uid: str
    period: str
    gross_salary: float
    net_salary: float
    avs_deduction: float | None = None
    lpp_deduction: float | None = None

class TVADeclarationNode(BaseNode):
    """Declaração trimestral ou anual de TVA (Décompte TVA)."""
    source_document_uid: str
    period: str
    total_sales: float
    tva_collected: float
    tva_deductible: float
    amount_due: float
