"""
Menir Core V5.1 - Central Async Runner (Watchdog)
The autonomous orchestrator that monitors incoming files, dispatches them
to appropriate skills, manages concurrency via Semaphores, runs reconciliation,
and handles compliance archiving.
"""

import asyncio
import logging
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Any


@dataclass
class SkillResult:
    success: bool
    nodes_and_edges: list[Any]
    message: str = ""


# --- O SIDECHAIN COMPRESSION (Logs) ---
# Impede que os arquivos de log engulam o HD do NAS rodopiando aos 50MB
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        RotatingFileHandler(
            "logs/menir_v5_core.log",
            maxBytes=50 * 1024 * 1024,  # 50 MB
            backupCount=2,
        ),
        logging.StreamHandler(),
    ],
)

# Importações Nucleares
from src.v3.core.reconciliation import ReconciliationEngine  # noqa: E402
from src.v3.menir_intel import MenirIntel  # noqa: E402
from src.v3.meta_cognition import MenirOntologyManager  # noqa: E402

# Imported Locally inside MenirAsyncRunner.__init__ to prevent Circular Imports

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
        # (Desativado B-04: Lógica movida diretamente para o worker de extensão)

        # 2. Habilidades de Processamento Genérico
        from src.v3.skills.camt053_skill import Camt053Skill
        from src.v3.skills.invoice_skill import InvoiceSkill

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
                dest_path = os.path.join(
                    archive_dir, f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
                )

            shutil.move(file_path, dest_path)
            logger.info(f"📁 Arquivo arquivado em compliance: {dest_path}")
        except Exception as e:
            logger.exception(f"⚠️ Erro ao arquivar o documento {file_path}: {e}")

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
                dest_path = os.path.join(
                    quarantine_dir, f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
                )

            shutil.move(file_path, dest_path)
            logger.warning(
                f"☣️ [Quarantine] Arquivo isolado fisicamente devido a Anomalia: {dest_path}"
            )
            
            # C-04: Quarentena Dupla (File + Graph Node)
            # Use hash as best-effort if available, else filename
            file_hash = filename.split('_')[0] if '_' in filename else filename
            self.ontology_manager.inject_entropy_anomaly(
                tenant, file_hash, "QuarantineEvent", f"Moved to {dest_path}", 1
            )
            
        except Exception as e:
            logger.exception(f"⚠️ Erro Crítico de I/O ao mover para Quarentena {file_path}: {e}")

    async def _process_single_file(self, file_path: str, tenant: str):
        """
        Worker isolado protegido por semáforo para processamento de um (1) documento.
        """
        from src.v3.core.schemas.identity import locked_tenant_context
        
        with locked_tenant_context(tenant):
            async with self.concurrency_limit:
                logger.info(f"⚙️ Processando Worker: {file_path}")
            try:
                # O Dispatcher nos diz o que é (FAST_LANE ou SLOW_LANE), mas a inteligência de saber
                # se é XML de banco ou Fatura fica a critério das extensões cruas primárias
                # Dado que o Camt053 só aceita XML, podemos rotear por MIME type puro aqui tbm.

                # Para simplificar o esqueleto: XML cai pra Banco, PDF/Imagem cai pra Fatura.
                ext = file_path.lower().rsplit(".", 1)[-1] if "." in file_path else ""

                if ext in ["xml", "camt053"]:
                    logger.info("➡️ Roteando para a Camt053Skill (Banco).")
                    # Tenant passado apenas no root do context
                    result = await self.camt053_skill.process_statement(file_path)
                else:
                    logger.info("➡️ Roteando para a InvoiceSkill (Faturamento).")
                    result = await self.invoice_skill.process_document(file_path)

                # Roteamento Físico Dinâmico (Compliance vs Anomaly Routing)
                if result.success:
                    self._archive_document(file_path, tenant)
                else:
                    logger.warning(f"❌ Falha de Skill no arquivo {file_path}: {result.message}")
                    self._quarantine_document(file_path, tenant)

            except Exception as e:
                logger.exception(f"Erro catastrófico no Worker para {file_path}: {e}")

    async def start_watchdog(self, inbox_dir: str, tenant: str):
        """
        O Loop de Vigilância Eterno.
        Varre diretórios, envia arrays pro Semaphore e, no final do lote, lança a Reconciliação.
        """
        # Levanta o Plano de Controle (Dual Mesh) em sub-tarefa do mesmo loop
        try:
            await self.synapse.start_servers(http_port=8080, socket_port=8081)
        except Exception as e:
            logger.exception(f"Failed to start Synapse Control Plane Servers: {e}")

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
                    logger.info(
                        f"📥 Detectados {len(pending_files)} novos documentos em {inbox_dir}"
                    )

                    # 0. The Circuit Breaker (Phase 32)
                    # Verifica a resiliência estrutural antes de gastar cota LLM
                    is_healthy = await asyncio.to_thread(self.ontology_manager.check_system_health)
                    if not is_healthy:
                        logger.error(
                            "🛑 WATCHDOG HALTED: System is operating with dead FATAL dependencies. Skipping processing cycle."
                        )
                        await asyncio.sleep(15)  # Penalidade de tempo antes de re-tentar
                        continue

                    # 1. Concorrência: TaskGroup isola o lançamento dos processos atrelados ao I/O (Semaphore(10))
                    # Enquanto a LLM é controlada internamente pelo Semaphore(50) no intel
                    async with asyncio.TaskGroup() as tg:
                        for file_path in pending_files:
                            tg.create_task(self._process_single_file(file_path, tenant))

                    # 2. Reconciliação Bate-Pronto: Após esvaziar a pasta, liga o Motor Cypher
                    logger.info(
                        "🔄 Esvaziamento concluído. Acionando Gatilho de Reconciliação do Lote."
                    )
                    from src.v3.core.schemas.identity import locked_tenant_context
                    
                    with locked_tenant_context(tenant):
                        await asyncio.to_thread(self.reconciliation_engine.run_matching_cycle)

            except Exception as e:
                logger.exception(f"🚨 Watchdog Loop Crash: {e}")

            # Dorme passivamente aguardando novos drops de arquivos da fiduciária (Cron-Like)
            await asyncio.sleep(5)


if __name__ == "__main__":

    async def boot_sequence():
        logger.info("🚀 Inicializando Menir Core V5.1 (Graph Self-Awareness Edition)...")
        # 1. Carrega o driver Neo4j
        import os

        from dotenv import load_dotenv

        from src.v3.meta_cognition import MenirOntologyManager

        load_dotenv(override=True)

        ontology = MenirOntologyManager()

        # 2. Inicia o Cérebro, passando o OntologyManager para ele ler a própria Persona do Banco
        intel = MenirIntel(ontology=ontology)

        # 3. Inicia o Watchdog Runner
        runner = MenirAsyncRunner(intel=intel, ontology_manager=ontology)

        # 4. Trava o loop principal monitorando a pasta Inbox (Tenant default: BECO)
        inbox_path = os.getenv("MENIR_INBOX", "Menir_Inbox/BECO")
        await runner.start_watchdog(inbox_dir=inbox_path, tenant="BECO")

    try:
        asyncio.run(boot_sequence())
    except KeyboardInterrupt:
        logger.info("🛑 Desligamento gracioso solicitado pelo Administrador.")
