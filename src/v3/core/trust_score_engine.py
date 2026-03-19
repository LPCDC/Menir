"""
TrustScoreEngine — Lógica de cálculo de confiança para documentos BECO.
Calcula um score de 0.0 a 1.0 baseado em integridade matemática, 
metadados e caminho de extração.
"""
from decimal import Decimal
from src.v3.core.schemas.financial import InvoiceData


def calculate_trust_score(data: InvoiceData) -> float:
    """
    Calcula o score de confiança final do documento.
    
    Regras refinadas (V2):
    - Base: extraction_confidence
    - Bonus QR: +0.20 (Selo de ouro de integridade física)
    - Bonus Meta: +0.10 IDE, +0.10 IBAN (Se for tipo pagamento)
    - Penalidade Fallback: -0.30 se não for tipo isento (Fatura s/ QR é suspeita)
    """
    score = float(data.extraction_confidence)
    
    # Bimodalidade: QR vs Fallback
    if data.extraction_path == "QR_DECODE":
        score += 0.20
    else:
        is_exempt = data.doc_type in [
            "Relevé bancaire", "Extrait de compte", "Police d'assurance", 
            "Certificat de salaire", "Déclaration d'impôt", "Extrait du registre",
            "Note de crédit", "Avis de crédit"
        ]
        if not is_exempt:
            score -= 0.30
            
    # Metadados Críticos
    if data.ide_number:
        score += 0.10
    
    if data.vendor_iban:
        score += 0.10
        
    return max(0.0, min(1.0, score))
