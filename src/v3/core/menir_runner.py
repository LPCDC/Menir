"""
Menir Core V5.1 - Central Async Runner (Watchdog)
The autonomous orchestrator that monitors incoming files, dispatches them
to appropriate skills, manages concurrency via Semaphores, runs reconciliation,
and handles compliance archiving.
"""
import os
import shutil
import asyncio
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# --- O SIDECHAIN COMPRESSION (Logs) ---
# Impede que os arquivos de log engulam o HD do NAS rodopiando aos 50MB
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        RotatingFileHandler(
            "logs/menir_v5_core.log", 
            maxBytes=50*1024*1024, # 50 MB
            backupCount=2
        ),
        logging.StreamHandler()
    ]
)

# Importações Nucleares
from src.v3.menir_intel import MenirIntel
from src.v3.meta_cognition import MenirOntologyManager
from src.v3.core.dispatcher import DocumentDispatcher
from src.v3.core.reconciliation import ReconciliationEngine
from src.v3.skills.invoice_skill import InvoiceSkill
from src.v3.skills.camt053_skill import Camt053Skill

logger = logging.getLogger("AsyncRunner")

class MenirAsyncRunner:
    """
    O Coração Assíncrono do Menir.
    Roda num servidor isolado escutando novos documentos para ingestão.
    """
    def __init__(self, intel: MenirIntel, ontology_manager: MenirOntologyManager):
        logger.info("⚡ Iniciando a Injeção de Dependências do MenirAsyncRunner...")
        self.intel = intel
        self.ontology_manager = ontology_manager
        
        # 1. Triagem e Roteamento
        self.dispatcher = DocumentDispatcher()
        
        # 2. Habilidades de Processamento Genérico
        self.invoice_skill = InvoiceSkill(self.intel, self.ontology_manager)
        self.camt053_skill = Camt053Skill(self.ontology_manager)
        
        # 3. Motor de Reconciliação
        self.reconciliation_engine = ReconciliationEngine(self.ontology_manager)
        
        # 4. Semáforo de Concorrência (RAM & Connection Pool Limits)
        self.concurrency_limit = asyncio.Semaphore(10)
        
        # 5. O Plano de Controle (Control Plane API)
        from src.v3.core.synapse import MenirSynapse
        self.synapse = MenirSynapse(self)

    def _archive_document(self, file_path: str, tenant: str):
        """
        Move o arquivo processado para a pasta de retenção de compliance (nFADP 10 anos).
        Path: Menir_Archive/{Tenant}/{Ano}/
        """
        try:
            current_year = str(datetime.now().year)
            archive_dir = os.path.join("Menir_Archive", tenant, current_year)
            os.makedirs(archive_dir, exist_ok=True)
            
            filename = os.path.basename(file_path)
            dest_path = os.path.join(archive_dir, filename)
            
            # Se já existir, sobrescrevemos ou damos append em timestamp.
            if os.path.exists(dest_path):
                name, ext = os.path.splitext(filename)
                dest_path = os.path.join(archive_dir, f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}")
                
            shutil.move(file_path, dest_path)
            logger.info(f"📁 Arquivo arquivado em compliance: {dest_path}")
        except Exception as e:
            logger.error(f"⚠️ Erro ao arquivar o documento {file_path}: {e}")

    def _quarantine_document(self, file_path: str, tenant: str):
        """
        Move o arquivo reprovado para a pasta Quarentena.
        Isso retira a fatura corrompida do Loop do Watchdog, evitando Deadlocks de I/O.
        Path: Menir_Inbox/Quarantine/{Tenant}/{Ano}/
        """
        try:
            current_year = str(datetime.now().year)
            quarantine_dir = os.path.join("Menir_Inbox", "Quarantine", tenant, current_year)
            os.makedirs(quarantine_dir, exist_ok=True)
            
            filename = os.path.basename(file_path)
            dest_path = os.path.join(quarantine_dir, filename)
            
            if os.path.exists(dest_path):
                name, ext = os.path.splitext(filename)
                dest_path = os.path.join(quarantine_dir, f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}")
                
            shutil.move(file_path, dest_path)
            logger.warning(f"☣️ [Quarantine] Arquivo isolado fisicamente devido a Anomalia: {dest_path}")
        except Exception as e:
            logger.error(f"⚠️ Erro Crítico de I/O ao mover para Quarentena {file_path}: {e}")

    async def _process_single_file(self, file_path: str, tenant: str):
        """
        Worker isolado protegido por semáforo para processamento de um (1) documento.
        """
        async with self.concurrency_limit:
            logger.info(f"⚙️ Processando Worker: {file_path}")
            try:
                # O Dispatcher nos diz o que é (FAST_LANE ou SLOW_LANE), mas a inteligência de saber 
                # se é XML de banco ou Fatura fica a critério das extensões cruas primárias
                # Dado que o Camt053 só aceita XML, podemos rotear por MIME type puro aqui tbm.
                
                # Para simplificar o esqueleto: XML cai pra Banco, PDF/Imagem cai pra Fatura.
                ext = file_path.lower().rsplit('.', 1)[-1] if '.' in file_path else ''
                
                if ext in ['xml', 'camt053']:
                    logger.info("➡️ Roteando para a Camt053Skill (Banco).")
                    result = await self.camt053_skill.process_statement(file_path, tenant)
                else:
                    logger.info("➡️ Roteando para a InvoiceSkill (Faturamento).")
                    result = await self.invoice_skill.process_document(file_path, tenant)

                # Roteamento Físico Dinâmico (Compliance vs Entropia)
                if result.success:
                    self._archive_document(file_path, tenant)
                else:
                    logger.warning(f"❌ Falha de Skill no arquivo {file_path}: {result.message}")
                    self._quarantine_document(file_path, tenant)
                    
            except Exception as e:
                logger.error(f"Erro catastrófico no Worker para {file_path}: {e}")

    async def start_watchdog(self, inbox_dir: str, tenant: str):
        """
        O Loop de Vigilância Eterno.
        Varre diretórios, envia arrays pro Semaphore e, no final do lote, lança a Reconciliação.
        """
        # Levanta o Plano de Controle (Dual Mesh) em sub-tarefa do mesmo loop
        try:
            await self.synapse.start_servers(http_port=8080, socket_port=8081)
        except Exception as e:
            logger.error(f"Failed to start Synapse Control Plane Servers: {e}")
            
        logger.info(f"👁️ Iniciando Watchdog para Inbox: {inbox_dir} (Tenant: {tenant})")
        
        while True:
            try:
                if not os.path.exists(inbox_dir):
                    os.makedirs(inbox_dir, exist_ok=True)
                    
                pending_files = [
                    os.path.join(inbox_dir, f) 
                    for f in os.listdir(inbox_dir) 
                    if os.path.isfile(os.path.join(inbox_dir, f))
                ]
                
                if pending_files:
                    logger.info(f"📥 Detectados {len(pending_files)} novos documentos em {inbox_dir}")
                    
                    # 1. Concorrência: TaskGroup isola o lançamento dos processos atrelados ao I/O (Semaphore(10))
                    # Enquanto a LLM é controlada internamente pelo Semaphore(50) no intel
                    async with asyncio.TaskGroup() as tg:
                        for file_path in pending_files:
                            tg.create_task(self._process_single_file(file_path, tenant))
                    
                    # 2. Reconciliação Bate-Pronto: Após esvaziar a pasta, liga o Motor Cypher
                    logger.info("🔄 Esvaziamento concluído. Acionando Gatilho de Reconciliação do Lote.")
                    # Como o Neo4j driver pode ser síncrono ou assíncrono envelopado, chamamos com to_thread.
                    await asyncio.to_thread(self.reconciliation_engine.run_matching_cycle, tenant)
                    
            except Exception as e:
                logger.error(f"🚨 Watchdog Loop Crash: {e}")
                
            # Dorme passivamente aguardando novos drops de arquivos da fiduciária (Cron-Like)
            await asyncio.sleep(5)

if __name__ == "__main__":
    pass
