from pydantic import BaseModel, Field
from typing import Optional
import logging
import os
from src.v3.menir_intel import MenirIntel

logger = logging.getLogger(__name__)

class DocumentClassification(BaseModel):
    document_type: str = Field(..., description="Tipo do documento (ex: INVOICE, BANK_STATEMENT, CONTRACT, LETTER, OTHER)")
    suggested_client_name: Optional[str] = Field(None, description="Nome do cliente sugerido se encontrado no texto")
    confidence: float = Field(..., description="Confiança na classificação (0.0 a 1.0)")
    language: str = Field(..., description="Idioma detectado no documento (ex: pt, fr, en, de)")

from src.v3.core.pdf_parser import classify_pdf_type

ALLOWED_TYPES = [
    "INVOICE_SUPPLIER", "INVOICE_CLIENT", "BANK_STATEMENT", "SALARY_SLIP", 
    "SALARY_CERTIFICATE", "EMPLOYMENT_CONTRACT", "TAX_DOCUMENT", "INSURANCE_DOCUMENT", 
    "COMMERCIAL_REGISTRY", "ADMINISTRATIVE_LETTER", "PAYMENT_CONFIRMATION", "OTHER"
]

from src.v3.core.trust_score_engine import calculate_trust_score
from src.v3.core.schemas.financial import InvoiceData
from decimal import Decimal

class DocumentClassifierSkill:
    def __init__(self, intel: MenirIntel):
        self.intel = intel

    async def classify_document(self, file_path: str) -> tuple[DocumentClassification, float, str]:
        """
        Classifica um documento usando Gemini Vision com lista estrita de tipos
        e determina o roteamento baseado no Trust Score.
        """
        prompt = (
            "Você é o Menir Document Classifier especializado em faturas suíças e documentos administrativos.\n\n"
            "Analise o documento e retorne APENAS UM único objeto JSON (não retorne listas, não retorne nada fora do objeto):\n"
            "1. document_type: DEVE ser um destes: " + ", ".join(ALLOWED_TYPES) + ".\n"
            "2. suggested_client_name: O nome da EMPRESA ou PESSOA (Creditor/Supplier).\n"
            "   - Procure por: 'Creditor: [Nome]' ou 'Supplier: [Nome]'.\n"
            "3. confidence: Score de 0.0 a 1.0.\n"
            "   - Se for 'ADMINISTRATIVE_LETTER' genérica ou documento ambíguo, confidence DEVE ser < 0.7.\n"
            "   - REGRA DE CONFIANÇA SEM PENALIDADE: Os tipos BANK_STATEMENT, COMMERCIAL_REGISTRY, e "
            "INSURANCE_DOCUMENT quando for atestado ou certificado, e qualquer documento identificado "
            "como nota de crédito ('Note de crédit', 'Avis de crédit'), NUNCA recebem penalidade de "
            "confiança por ausência de QR Code. A ausência de QR nesses tipos é comportamento esperado "
            "e correto — não reduza o score de confiança por essa razão.\n"
            "4. language: Abreviação de 2 letras do idioma (pt, fr, en, de).\n\n"
            "DOCUMENTO:\n"
        )

        from src.v3.core.concurrency import run_in_custom_executor, cpu_pool, pdf_mem_semaphore
        try:
            # Detecta se é PDF e extrai as partes - CPU BOUND
            async with pdf_mem_semaphore:
                pdf_type, raw_parts = await run_in_custom_executor(cpu_pool, classify_pdf_type, file_path)
            
            result = await self.intel.structured_inference(
                prompt=prompt,
                raw_parts=raw_parts,
                response_schema=DocumentClassification
            )
            
            # Validação Estrita de Tipo
            if result.document_type not in ALLOWED_TYPES:
                logger.warning(f"Tipo inválido '{result.document_type}' retornado por Gemini. Coagindo para OTHER.")
                result.document_type = "OTHER"
                result.confidence = 0.3
            
            # Cálculo de Trust Score (Fast Lane vs Quarentena)
            # Criamos um mock parcial de InvoiceData para o engine
            # EXTRACTION_PATH depende do bimodal detector (DIGITAL -> "QR_DECODE" em potencial, SCANNED -> "GEMINI_FALLBACK")
            p_type = pdf_type.value if hasattr(pdf_type, "value") else str(pdf_type)
            path = "QR_DECODE" if p_type == "DIGITAL" else "GEMINI_FALLBACK"
            
            # Nota: transformamos os tipos de DocumentClassification para os tipos de InvoiceData se necessário
            # InvoiceData temporário: criado apenas para alimentar o trust_score_engine, não persiste no grafo.
            mock_data = InvoiceData(
                uid="temp", project="TEMP", source_document_uid="temp",
                vendor_name=result.suggested_client_name or "Unknown",
                doc_type="Facture QR" if result.document_type == "INVOICE_SUPPLIER" else "Note de frais",
                language=result.language,
                currency="CHF", issue_date="2000-01-01", subtotal=0, total_amount=0, items=[],
                extraction_path=path,
                extraction_confidence=Decimal(str(result.confidence))
            )
            
            score = calculate_trust_score(mock_data)
            target = "PRODUCTION" if score >= 0.85 else "QUARANTINE"
            
            logger.info(f"Roteamento para {file_path}: {target} (Score: {score:.2f})")
            return result, float(score), target
        except Exception as e:
            logger.error(f"Falha na classificação do documento {file_path}: {e}")
            return DocumentClassification(
                document_type="OTHER",
                suggested_client_name=None,
                confidence=0.0,
                language="??"
            ), 0.0, "QUARANTINE"
