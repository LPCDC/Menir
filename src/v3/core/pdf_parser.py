import enum
import logging
from typing import Any
import os
import re
from pypdf import PdfReader

logger = logging.getLogger("PdfClassifier")

class PdfType(enum.Enum):
    DIGITAL = "DIGITAL"
    SCANNED = "SCANNED"
    HYBRID = "HYBRID"


def classify_pdf_type(file_path: str) -> tuple[PdfType, list[Any]]:
    """
    Classifica um PDF e extrai seu conteúdo numérico/visual de forma transparente.
    Retorna o tipo detectado e uma lista 'Parts' (texto cru ou PIL Images) pronta para o Gemini.
    """
    try:
        reader = PdfReader(file_path)
        pages_text = []
        for page in reader.pages:
            t = page.extract_text() or ""
            pages_text.append(t)
    except Exception as e:
        logger.warning(f"Erro ao extrair texto nativo com pypdf: {e}. Fallback para SCANNED.")
        return convert_to_scanned_parts(file_path)

    total_chars = sum(len(text) for text in pages_text)
    num_pages = len(pages_text) or 1
    chars_per_page = total_chars / num_pages

    if chars_per_page < 50:
        logger.info(f"Classificado como SCANNED (< 50 chars/page). Usando Visão para {file_path}")
        return convert_to_scanned_parts(file_path)

    full_text = "\n".join(pages_text)

    # Verifica se há alta fragmentação ou excesso de caracteres estranhos
    # Ex: muitas quebras de linha soltas ou mais de 10% do texto em não-alfanuméricos estranhos fora do comum
    suspicious_chars = len(re.findall(r"[^\w\s\.,;:!?\-+*=\(\)\[\]/\\@#$%&|<>]", full_text))
    newline_ratio = full_text.count("\n") / max(1, total_chars)

    if newline_ratio > 0.25 or (total_chars > 0 and suspicious_chars / total_chars > 0.05):
        logger.info(f"Classificado como HYBRID (Fragmentado). Rearmando prompt para {file_path}")
        hybrid_prompt = (
            "INSTRUÇÃO DO CLASSIFICADOR HYBRID:\n"
            "O texto a seguir foi extraído de um PDF digital, mas seu layout visual quebrou "
            "as linhas e palavras de maneira imprevisível. Realize a reordenação semântica mental "
            "antes de extrair as entidades.\n\n"
        )
        return PdfType.HYBRID, [hybrid_prompt + full_text]

    logger.info(f"Classificado como DIGITAL. {file_path}")
    return PdfType.DIGITAL, [full_text]

def convert_to_scanned_parts(file_path: str) -> tuple[PdfType, list[Any]]:
    try:
        from pdf2image import convert_from_path
        # Converte em 200 DPI para economizar RAM/Tamanho mas mantendo boa leitura OCR
        images = convert_from_path(file_path, dpi=200)
        return PdfType.SCANNED, list(images)
    except Exception as e:
        logger.error(f"Falha ao converter PDF Scanned para imagem via pdf2image/Poppler: {e}")
        # Mesmo se falhar, tentamos jogar no Gemini Vision a path crua comprimida (fallback do InvoiceSkill)
        # O Dispatcher não precisa saber, ele passará o file_path pro fallback
        raise RuntimeError(f"Poppler/pdf2image conversion failed: {e}")
