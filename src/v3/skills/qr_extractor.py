import os
import asyncio
import logging
from src.v3.skills.swiss_qr_parser import SwissQRParser, SwissQRParserError

logger = logging.getLogger("CresusQRExtractor")

def _sync_extract_qr(pdf_path: str) -> dict | None:
    if not os.path.exists(pdf_path):
        logger.warning(f"Extrator QR falhou: Arquivo nao encontrado {pdf_path}")
        return None
        
    try:
        import pypdfium2 as pdfium
        from pyzbar.pyzbar import decode
        from PIL import Image
    except ImportError as e:
        logger.warning(f"Dependencias de extracao QR (pypdfium2/pyzbar) nao instaladas: {e}")
        return None

    try:
        doc = pdfium.PdfDocument(pdf_path)
        if len(doc) == 0:
            logger.warning("Extrator QR falhou: PDF vazio.")
            return None
            
        # O padrao SIX v2.3 dita que a fatura QR esta sempre no rodape da ultima pagina
        last_page = doc[len(doc) - 1]
        
        # 300 DPI e o minimo mandatado pelas best practices para leitura confiavel de QRs
        bitmap = last_page.render(scale=300/72) 
        pil_image = bitmap.to_pil()
        
        # PYZBAR processa melhor em Grayscale
        grayscale_image = pil_image.convert('L')
        
        decoded_symbols = decode(grayscale_image)
        
        for symbol in decoded_symbols:
            payload = symbol.data.decode("utf-8")
            if payload.startswith("SPC"):
                # Encontramos um conteudo valido Swiss QR
                parser = SwissQRParser()
                return parser.parse(payload)

        # Se iterou tudo e nao achou ou se nao tinha simbolos
        logger.warning(f"Extrator QR falhou: Nenhum QR Code padrao SIX/SPC encontrado em {pdf_path}")
        return None
        
    except SwissQRParserError as sqe:
        logger.warning(f"Extrator QR falhou na validacao contabil: {sqe}")
        return None
    except Exception as e:
        logger.warning(f"Extrator QR encontrou panico interno silencioso: {e}")
        return None
    finally:
        # Guarantee doc closure if initialized to avoid memory leaks native C bindings hold
        if 'doc' in locals():
            doc.close()

async def extract_qr_from_pdf(pdf_path: str) -> dict | None:
    """
    Assincronamente extrai, decodifica e analisa um Swiss QR Code Type S (SIX v2.3) de um PDF.
    Isola a carga pesada de CPU/RAM (pypdfium2 renders e pyzbar decodes) da main event loop via to_thread.
    Retorna None silenciosamente se o codigo estiver corrompido, ilegivel, ou se faltar o documento.
    """
    return await asyncio.to_thread(_sync_extract_qr, pdf_path)
