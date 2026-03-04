"""
Menir Core V5.1 - Interface Contracts (Protocols/ABCs)
Providing structural guarantees for Dependency Injection across modules.
"""

from typing import Protocol, runtime_checkable
from src.v3.core.menir_runner import SkillResult

@runtime_checkable
class DocumentExtractionSkill(Protocol):
    """
    Contrato rigoroso para qualquer Skill que processe documentos na Engine Menir.
    (Ex: InvoiceSkill, Camt053Skill)
    """
    async def process_document(self, file_path: str) -> SkillResult:
        ...

@runtime_checkable
class ReconciliationProtocol(Protocol):
    """
    Contrato para o motor de Reconciliação Cypher.
    """
    def run_matching_cycle(self) -> None:
        ...

@runtime_checkable
class EventRunner(Protocol):
    """
    Contrato do Control Plane para o Synapse.
    """
    def _quarantine_document(self, file_path: str, tenant: str) -> None:
        ...
    def flush_quarantine(self) -> None:
        ...
