"""
Menir Core V5.1 - Bimodal Document Dispatcher
Routes ingestion payloads between FAST_LANE (Deterministic parsers / Clean Text PDFs)
and SLOW_LANE (Heavy LLM Vision for Scans and Photos).
"""

import logging
import mimetypes
import os
from typing import Literal

from pypdf import PdfReader, errors

logger = logging.getLogger("MenirDispatcher")


class DocumentDispatcher:
    """
    Rapid triage system that determines the downstream processing lane
    in milliseconds without deeply extracting the whole document.
    """

    def __init__(self, text_threshold: int = 150):
        self.text_threshold = text_threshold
        # Adding common xml extensions just in case mimetypes fails
        mimetypes.add_type("text/xml", ".xml")

    def analyze_payload(self, file_path: str) -> Literal["FAST_LANE", "SLOW_LANE"]:
        """
        Analisa o arquivo e decide a fila de processamento.
        - FAST_LANE: Arquivos XML (Camt053) ou PDFs nativos com camada de texto.
        - SLOW_LANE: Imagens (PNG/JPG) ou PDFs escaneados (sem texto extraível).
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found for triage: {file_path}")
            return "SLOW_LANE"  # Fall forward to standard fallback

        mime_type, _ = mimetypes.guess_type(file_path)
        ext = file_path.lower().rsplit(".", 1)[-1] if "." in file_path else ""

        # 1. XML Bancário ou ERP data (Camt053, CRE, CSV)
        if ext in ["xml", "csv", "cre"] or mime_type in ["text/xml", "application/xml", "text/csv"]:
            logger.info(f"⚡ [FAST_LANE] XML/Data file detected: {file_path}")
            return "FAST_LANE"

        # 2. Imagens Brutas de WhatsApp, etc (Receipts and photos)
        if mime_type and mime_type.startswith("image/"):
            logger.info(f"🐢 [SLOW_LANE] Image file detected, sending to Vision LLM: {file_path}")
            return "SLOW_LANE"

        # 3. PDF Parsing (Determinar se tem camada OCR Nativa ou não)
        if ext == "pdf" or mime_type == "application/pdf":
            try:
                reader = PdfReader(file_path)

                if len(reader.pages) == 0:
                    return "SLOW_LANE"

                total_text = ""
                # Avalia no máximo as 3 primeiras páginas para ser ultra-rápido (O(1))
                check_pages = min(3, len(reader.pages))

                for i in range(check_pages):
                    page_text = reader.pages[i].extract_text()
                    if page_text:
                        total_text += page_text

                    # Early exit se já bateu o threshold
                    if len(total_text.strip()) >= self.text_threshold:
                        logger.info(
                            f"⚡ [FAST_LANE] Native Text PDF detected (Early exit): {file_path}"
                        )
                        return "FAST_LANE"

                # Se após as 3 páginas de teste não tiver texto, é um PDF montado com Scans/Fotos (Sem OCR)
                logger.info(
                    f"🐢 [SLOW_LANE] Scanned PDF detected, sending to Vision LLM: {file_path}"
                )
                return "SLOW_LANE"

            except errors.PdfReadError as e:
                logger.warning(f"⚠️ PDF Read Error during triage, falling back to SLOW_LANE: {e}")
                return "SLOW_LANE"
            except Exception as e:
                logger.warning(f"⚠️ Unexpected Error parsing PDF during triage: {e}")
                return "SLOW_LANE"

        # 4. Fallback Default para segurança (Joga para o LLM tentar resolver)
        logger.warning(f"❓ Standard Fallback. Unknown file type {mime_type} routed to SLOW_LANE.")
        return "SLOW_LANE"


if __name__ == "__main__":
    # Teste unitário manual isolado
    import tempfile

    dispatcher = DocumentDispatcher()

    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp_xml:
        tmp_xml.write(b"<xml></xml>")
        xml_path = tmp_xml.name

    print(f"Testing XML: {dispatcher.analyze_payload(xml_path)}")
    os.remove(xml_path)
