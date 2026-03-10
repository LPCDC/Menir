import logging
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from src.v3.menir_intel import MenirIntel
from src.v3.meta_cognition import MenirOntologyManager
from src.v3.core.menir_runner import SkillResult

logger = logging.getLogger("DocumentDispatcher")

class DispatcherClassification(BaseModel):
    model_config = ConfigDict(extra="forbid")
    doc_type: str = Field(description="Tipo de documento extraído, 1 dos 28 possíveis.")
    confidence_score: float = Field(description="Score de confiança de 0.0 a 1.0")


class DocumentDispatcher:
    """
    Roteador cognitivo multiclasse. Extrai apenas a primeira página para classificação rápida.
    Despacha para a Skill correta ou para Quarentena usando a régua de confiança.
    """

    def __init__(self, intel: MenirIntel, ontology_manager: MenirOntologyManager):
        self.intel = intel
        self.ontology_manager = ontology_manager

    def _quarantine(self, tenant: str, file_hash: str, doc_type: str, reason: str, override_status: str = 'QUARANTINE'):
        safe_tenant = tenant.replace("`", "")
        cypher = f"""
        MERGE (d:Document:`{safe_tenant}` {{file_hash: $file_hash}})
        SET d.status = $status,
            d.quarantine_reason = $reason,
            d.doc_type = $doc_type,
            d.quarantined_at = datetime()
        """
        try:
            with self.ontology_manager.driver.session() as session:
                with session.begin_transaction() as tx:
                    tx.run(cypher, file_hash=file_hash, reason=reason, doc_type=doc_type, status=override_status)
        except Exception as query_exc:
            logger.exception(f"Falha ao registrar quarentena do dispatcher no Neo4j: {query_exc}")

    async def route_document(self, file_path: str, file_hash: str, text: str, tenant: str) -> SkillResult:
        """
        Rota principal. Executa `classify` e obedece The Graduated Confidence Rule.
        """
        try:
            classification = await self.classify(text)
        except Exception as e:
            self._quarantine(tenant, file_hash, "Unknown", "Classification_Failed")
            return SkillResult(success=False, nodes_and_edges=[], message=str(e))
        
        doc_type = classification.doc_type
        score = classification.confidence_score
        
        logger.info(f"🧭 Dispatcher: {doc_type} (Score: {score})")

        # Regra 1: Abaixo de 0.60
        if score < 0.60:
            self._quarantine(tenant, file_hash, doc_type, "LOW_CONFIDENCE")
            return SkillResult(success=False, nodes_and_edges=[], message=f"Abortado: LOW_CONFIDENCE ({score})")
        
        # Regra 2: Entre 0.60 e 0.85
        if score <= 0.85:
            self._quarantine(tenant, file_hash, doc_type, f"LOW_CONFIDENCE_CLASSIFICATION (Score: {score})")
            return SkillResult(success=False, nodes_and_edges=[], message=f"Quarentena Humana: Confidence {score}")
            
        # Regra 3: Acima de 0.85 (Roteamento Direto ou Stub)
        salary_types = ["Fiche de salaire", "Certificat de salaire"]
        rh_types = ["Contrat", "Police d'assurance", "Décompte AVS", "Décompte LPP"]
        invoice_types = ["Facture", "Note de crédit", "Rappel", "Ticket de caisse", "Note de frais", "Quittance", "Reçu", "BVR", "Facture QR"]
        camt_types = ["Relevé bancaire", "Extrait de compte", "Avis de débit", "Avis de crédit"]
        
        if doc_type in salary_types or doc_type in rh_types:
            # Stubs transparentes para RH e Salário (Pass-through)
            self._quarantine(tenant, file_hash, doc_type, "Pending Skill Implementation", override_status="PENDING_SKILL")
            return SkillResult(success=True, nodes_and_edges=[], message=f"Stub acionado: Documento retido em PENDING_SKILL ({doc_type}).")
            
        elif doc_type in invoice_types:
            return SkillResult(success=True, nodes_and_edges=[], message="ROUTE_TO: invoice_skill")
            
        elif doc_type in camt_types:
            return SkillResult(success=True, nodes_and_edges=[], message="ROUTE_TO: camt053_skill")
            
        else:
            # Qualquer outro tipo não mapeado (Ex: Tax etc) também cai no STUB genericamente
            self._quarantine(tenant, file_hash, doc_type, "Skill not defined yet", override_status="PENDING_SKILL")
            return SkillResult(success=True, nodes_and_edges=[], message=f"Stub acionado: PENDING_SKILL genérico para ({doc_type}).")

    async def classify(self, document_text: str) -> DispatcherClassification:
        # Simula extração da primeira página pegando os primeiros ~2000 caracteres
        first_page = document_text[:2000]

        prompt = f"""
        Classifique o seguinte documento com base no texto da primeira página.
        Tipos possíveis: "Facture", "Note de crédit", "Rappel", "Ticket de caisse", "Relevé bancaire", 
        "Contrat", "Police d'assurance", "Déclaration d'impôt", "Fiche de salaire", 
        "Note de frais", "Quittance", "Reçu", "Extrait de compte", "BVR", "Facture QR", 
        "Avis de débit", "Avis de crédit", "Décompte TVA", "Décompte LPP", "Décompte AVS", 
        "Certificat de salaire", "Bilan", "Compte de resultado", "Grand livre", "Journal", 
        "Balance", "Extrait du registre", "Offre".
        
        TEXTO:
        {first_page}
        """

        try:
            return await self.intel.structured_inference(prompt=prompt, response_schema=DispatcherClassification)
        except Exception:
            logger.exception("Falha na classificação inicial do Dispatcher.")
            raise
