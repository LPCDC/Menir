import os
import time
import shutil
import asyncio
import logging
import hashlib
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.v3.menir_intel import MenirIntel
from src.v3.meta_cognition import MenirOntologyManager
from src.v3.core.dispatcher import DocumentDispatcher
from src.v3.core.schemas.identity import locked_tenant_context
from src.v3.skills.invoice_skill import InvoiceSkill

# Configura o log básico para o processo em background
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MenirWatcher")

class MenirFolderHandler(FileSystemEventHandler):
    def __init__(self, watch_folder, tenant, intel, ontology):
        self.watch_folder = watch_folder
        self.tenant = tenant
        self.intel = intel
        self.ontology = ontology
        self.dispatcher = DocumentDispatcher(intel, ontology)
        self.invoice_skill = InvoiceSkill(intel, ontology)
        
        self.processed_folder = os.path.join(self.watch_folder, "processed")
        self.quarantine_folder = os.path.join(self.watch_folder, "quarantine")
        
        os.makedirs(self.processed_folder, exist_ok=True)
        os.makedirs(self.quarantine_folder, exist_ok=True)
        
        # Loop assíncrono mantido para não bloquear a thread do watchdog
        self.loop = asyncio.new_event_loop()
        
    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = event.src_path
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in [".pdf", ".png", ".jpg"]:
            logger.info(f"Novo arquivo detectado: {file_path}")
            # Delega para a corrotina assíncrona
            asyncio.run_coroutine_threadsafe(self.process_file_async(file_path), self.loop)

    async def process_file_async(self, file_path: str):
        try:
            # Short sleep para garantir que o SO terminou a escrita
            await asyncio.sleep(1)
            
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            file_hash = hashlib.sha256(file_bytes).hexdigest()
            filename = os.path.basename(file_path)

            logger.info(f"Iniciando isolamento galvânico para Tenant: {self.tenant}")
            with locked_tenant_context(self.tenant):
                # Extrai texto rápido para o Dispatcher
                from pypdf import PdfReader
                try:
                    reader = PdfReader(file_path)
                    text_content = "\\n".join(page.extract_text() or "" for page in reader.pages)
                except Exception:
                    text_content = "" # Fallback se falhar
                    
                # 1. Roteamento Multiclasse do Dispatcher
                dispatch_result = await self.dispatcher.route_document(file_path, file_hash, text_content, self.tenant)
                
                if dispatch_result.success and "ROUTE_TO: invoice_skill" in dispatch_result.message:
                    # 2. Processamento Principal (Skill)
                    result = await self.invoice_skill.process_document(file_path)
                    
                    if result.success:
                        self.move_to_processed(file_path, filename)
                    else:
                        reason = result.message.replace(" ", "_").replace(":", "").replace("/", "_")
                        self.move_to_quarantine(file_path, filename, reason[:50])
                else:
                    # Falha no dispatch ou routing para skill ainda não testada pelo watcher
                    reason = dispatch_result.message.replace(" ", "_").replace(":", "").replace("/", "_")
                    self.move_to_quarantine(file_path, filename, reason[:50])

        except Exception as e:
            logger.exception(f"Erro fatal processando {file_path}")
            self.move_to_quarantine(file_path, os.path.basename(file_path), "Fatal_Error")

    def move_to_processed(self, file_path: str, filename: str):
        dest = os.path.join(self.processed_folder, filename)
        if os.path.exists(dest):
            dest = os.path.join(self.processed_folder, f"{int(time.time())}_{filename}")
        shutil.move(file_path, dest)
        logger.info(f"📁 Movido para Processed: {dest}")

    def move_to_quarantine(self, file_path: str, filename: str, reason: str):
        name, ext = os.path.splitext(filename)
        safe_reason = "".join([c for c in reason if c.isalnum() or c in ('_', '-')])
        dest_filename = f"{name}_{safe_reason}{ext}"
        dest = os.path.join(self.quarantine_folder, dest_filename)
        
        if os.path.exists(dest):
            dest = os.path.join(self.quarantine_folder, f"{int(time.time())}_{dest_filename}")
        try:
            shutil.move(file_path, dest)
            logger.warning(f"☣️ Movido para Quarentena: {dest}")
        except Exception as e:
            logger.error(f"Erro ao mover para quarentena {file_path}: {e}")

def start_watcher():
    load_dotenv()
    
    watch_folder = os.getenv("MENIR_WATCH_FOLDER", "Menir_Inbox")
    tenant = os.getenv("MENIR_WATCH_TENANT", "BECO")
    
    if not os.path.exists(watch_folder):
        os.makedirs(watch_folder, exist_ok=True)
        
    logger.info("Initializing Menir Cognition Cores...")
    intel = MenirIntel()
    ontology = MenirOntologyManager()

    handler = MenirFolderHandler(watch_folder, tenant, intel, ontology)
    
    # Inicia a thread do asyncio em background (para despachar as corrotinas)
    import threading
    t = threading.Thread(target=handler.loop.run_forever, daemon=True)
    t.start()

    observer = Observer()
    observer.schedule(handler, watch_folder, recursive=False)
    observer.start()
    
    logger.info(f"👀 Menir Standalone Folder Watcher iniciado.")
    logger.info(f"📁 Vigiando: {os.path.abspath(watch_folder)}")
    logger.info(f"🛡️ Default Tenant: {tenant}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Watcher interrompido pelo usuário.")
        handler.loop.call_soon_threadsafe(handler.loop.stop)
    observer.join()

if __name__ == "__main__":
    start_watcher()
