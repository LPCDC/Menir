"""
Menir Core V5.1 - Payload Compressor (I/O Throttle Shield)
Compresses massive images and scanned PDFs into lightweight 
standardized JPEGs to prevent NAS TCP congestion during Tax Season.
"""
import os
import io
import uuid
import tempfile
import logging
from PIL import Image
import fitz # PyMuPDF
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger("PayloadCompressor")

class PayloadCompressor:
    """
    Motor de Downsampling agressivo.
    Transforma lixo digital (Scans de 10MB) em sinal limpo (<1MB) para a Vision API.
    """
    def __init__(self, max_dimension: int = 2048, jpeg_quality: int = 85, pdf_dpi: int = 150):
        self.max_dimension = max_dimension
        self.jpeg_quality = jpeg_quality
        self.pdf_dpi = pdf_dpi
        
        # Temp dir garantido pela OS, limpo pelos ciclos
        self.temp_dir = tempfile.gettempdir()

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=3))
    def compress_for_vision(self, file_path: str) -> str:
        """
        Analisa a extensão e aplica o downsampling físico do documento.
        Retorna o caminho absoluto do arquivo `.jpg` otimizado gerado.
        Lança exceção em caso de arquivo corrompido, ativando a Quarentena da Skill.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado para compressão: {file_path}")
            
        ext = file_path.lower().rsplit('.', 1)[-1] if '.' in file_path else ''
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        logger.info(f"🗜️ Iniciando compressão. Tamanho original: {file_size_mb:.2f} MB")

        # Gerar nome temporário único
        out_filename = f"menir_opt_{uuid.uuid4().hex[:8]}.jpg"
        out_path = os.path.join(self.temp_dir, out_filename)

        if ext in ['pdf']:
            self._compress_pdf(file_path, out_path)
        elif ext in ['jpg', 'jpeg', 'png', 'webp', 'heic']:
            self._compress_image(file_path, out_path)
        else:
            # Fallback pass-through se for um tipo obscuro, embora a Triagem já deva ter filtrado
            logger.warning(f"Extensão invisível ao Compressor: {ext}. Tentando abrir via Pillow fallback.")
            self._compress_image(file_path, out_path)
            
        final_size_mb = os.path.getsize(out_path) / (1024 * 1024)
        logger.info(f"✅ Compressão O(1) concluída. Resultante: {final_size_mb:.2f} MB")
        
        return out_path

    def _compress_image(self, in_path: str, out_path: str):
        """Redimensiona via Pillow e salva em JPEG 85%"""
        try:
            with Image.open(in_path) as img:
                # Converter para RGB se for PNG com transparência
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                    
                # Aplicar resize mantendo o Aspect Ratio (thumbnail altera in-place)
                img.thumbnail((self.max_dimension, self.max_dimension), Image.Resampling.LANCZOS)
                
                # Salvar agressivamente
                img.save(out_path, format="JPEG", quality=self.jpeg_quality, optimize=True)
        except Exception as e:
            logger.error(f"Falha ao comprimir Imagem {in_path}: {e}")
            raise RuntimeError(f"Compressão Imagem Falhou: {e}")

    def _compress_pdf(self, in_path: str, out_path: str):
        """Converte a PRIMEIRA página do PDF em uma matrix de Pixels Otimizada (150 DPI)"""
        try:
            doc = fitz.open(in_path)
            if len(doc) == 0:
                raise ValueError("PDF Vazio")
                
            # Renderizar a página 0. Para faturas, 99% das vezes o "Total" tá na primeira ou segunda folha.
            # Aqui vamos ser puristas de rede e mandar só a primeira na Slow Lane como discutido.
            page = doc.load_page(0)
            
            # Matriz de resolução (ex: 150 DPI gera uma escala de ~2.0x num PDF padrão A4)
            zoom = self.pdf_dpi / 72.0 
            mat = fitz.Matrix(zoom, zoom)
            
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # PyMuPDF pode salvar direto, mas vamos repassar pro Pillow para garantir o pipeline JPEG 85%
            img_data = pix.tobytes("png")
            with Image.open(io.BytesIO(img_data)) as img:
                img = img.convert("RGB")
                img.thumbnail((self.max_dimension, self.max_dimension), Image.Resampling.LANCZOS)
                img.save(out_path, format="JPEG", quality=self.jpeg_quality, optimize=True)
                
            doc.close()
        except Exception as e:
            logger.error(f"Falha ao comprimir PDF {in_path}: {e}")
            raise RuntimeError(f"Compressão PDF Falhou: {e}")

if __name__ == "__main__":
    pass
