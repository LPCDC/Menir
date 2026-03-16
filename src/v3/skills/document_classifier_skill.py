from pydantic import BaseModel, Field
from typing import Optional
import logging
import os
from src.v3.menir_intel import MenirIntel

logger = logging.getLogger(__name__)

class DocumentClassification(BaseModel):
    document_type: str = Field(..., description="Tipo do documento (ex: INVOICE, CONTRACT, LETTER, OTHER)")
    suggested_client_name: Optional[str] = Field(None, description="Nome do cliente sugerido se encontrado no texto")
    confidence: float = Field(..., description="Confiança na classificação (0.0 a 1.0)")

from src.v3.core.pdf_parser import classify_pdf_type

class DocumentClassifierSkill:
    def __init__(self, intel: MenirIntel):
        self.intel = intel

    async def classify_document(self, file_path: str) -> DocumentClassification:
        """
        Classifica um documento usando Gemini Vision.
        """
        prompt = (
            "Você é o Menir Document Classifier especializado em faturas suíças.\n\n"
            "Analise o documento e retorne APENAS UM único objeto JSON (não retorne listas, não retorne nada fora do objeto):\n"
            "1. document_type: INVOICE, CONTRACT, LETTER, ou OTHER.\n"
            "2. suggested_client_name: O nome da EMPRESA ou PESSOA (Creditor/Supplier).\n"
            "   - Procure por: 'Creditor: [Nome]' ou 'Supplier: [Nome]'.\n"
            "3. confidence: Score de 0.0 a 1.0.\n"
            "   - Se for uma 'LETTER' genérica, confidence DEVE ser < 0.7.\n\n"
            "DOCUMENTO:\n"
        )

        try:
            # Detecta se é PDF e extrai as partes (Imagens ou Texto)
            _, raw_parts = classify_pdf_type(file_path)
            
            # Força o prompt como primeira parte explicitamente
            result = await self.intel.structured_inference(
                prompt=prompt,
                raw_parts=raw_parts,
                response_schema=DocumentClassification
            )
            logger.info(f"Classificação RAW para {file_path}: {result}")
            return result
        except Exception as e:
            logger.error(f"Falha na classificação do documento {file_path}: {e}")
            return DocumentClassification(
                document_type="OTHER",
                suggested_client_name=None,
                confidence=0.0
            )
