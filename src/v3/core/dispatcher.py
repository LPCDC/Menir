import logging
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from src.v3.menir_intel import MenirIntel

logger = logging.getLogger("DocumentDispatcher")


class DispatcherClassification(BaseModel):
    model_config = ConfigDict(extra="forbid")
    doc_type: str = Field(description="Tipo de documento extraído, 1 dos 28 possíveis.")
    confidence_score: float = Field(description="Score de confiança de 0.0 a 1.0")


class DocumentDispatcher:
    """
    Roteador cognitivo. Extrai apenas a primeira página para classificação rápida.
    Despacha para a Skill correta.
    """

    def __init__(self, intel: MenirIntel):
        self.intel = intel

    async def classify(self, document_text: str) -> DispatcherClassification:
        logger.info("Classificando documento via Dispatcher...")
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
            # Chamada estruturada (já existe em MenirIntel na V2)
            # Como a assinatura depende do MenirIntel, usamos generate_content se o wrapper falhar
            return await self.intel.structured_inference(prompt, DispatcherClassification)
        except Exception as e:
            logger.exception("Falha na classificação inicial do Dispatcher.")
            raise

