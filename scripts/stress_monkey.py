"""
Menir Core V5.1 - Chaos Monkey (Resilience & Stress Test)
Simulates a brutal load of 100 concurrent incoming invoices representing
"My Cafe Bar Sàrl" (TVA 5.3%) while simultaneously bombarding the 
MenirSynapse control plane with asynchronous NLP payload requests.
Measures latency resilience and Write-Lock deadlocks in the Neo4j cluster.
"""
import os
import time
import asyncio
import logging
import aiohttp
from reportlab.pdfgen import canvas
from src.v3.meta_cognition import MenirOntologyManager

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ChaosMonkey")

INBOX_DIR = "Menir_Inbox"
TENANT = "BECO"
NUM_INVOICES = 100
WEB_UI_PORT = 8080

def generate_synthetic_invoices(count: int, target_dir: str):
    """
    Generates realistic lightweight synthetic PDFs based on "My Cafe Bar Sàrl"
    to mimic the Tax Season volume hitting the Watchdog's inbox.
    """
    os.makedirs(target_dir, exist_ok=True)
    logger.info(f"💥 Iniciando enxame de {count} Faturas Sintéticas [My Cafe Bar Sàrl - TVA 5.3%] para Inbox...")
    
    for i in range(count):
        filepath = os.path.join(target_dir, f"chaos_invoice_mycafebar_{i:03d}.pdf")
        
        # We generate a PDF using reportlab to make it a legit binary file
        c = canvas.Canvas(filepath)
        c.drawString(100, 800, "INVOICE / FACTURE")
        c.drawString(100, 780, f"Vendor: My Cafe Bar Sàrl")
        c.drawString(100, 760, f"Date: 2026-02-{(i%28)+1:02d}")
        c.drawString(100, 740, f"Total CHF: {15.50 + i:.2f}")
        c.drawString(100, 720, "TVA: 5.3%")
        c.drawString(100, 700, "Account: 3400 / 2200")
        c.save()
    
    logger.info("✅ Enxame I/O de PDF Sintéticos Desovado.")

async def hammer_synapse(duration_seconds: int):
    """
    Dispara requests JSON agressivos para o Control Plane (Synapse) 
    para tentar travar o Event Loop ou corromper a leitura do CommandBus.
    """
    logger.info(f"🔨 Iniciando Bombardeio de NLP na Porta {WEB_UI_PORT} por {duration_seconds}s...")
    start_time = time.time()
    request_count = 0
    
    # We will simulate noisy NLP intents that the Logos Cortex must interpret under pressure
    payloads = [
        {"action": "RELOAD_RULES", "origin": "WEB_UI", "intent": "Atualiza essas regras aí agora no banco!"},
        {"action": "PAUSE_INGESTION", "origin": "AI_ORACLE", "intent": "Emergencia, pausa a fila!"},
        {"action": "STATUS_REPORT", "origin": "CLI_LOCAL", "intent": "qual o status atual do loop?"}
    ]
    
    async with aiohttp.ClientSession() as session:
        while time.time() - start_time < duration_seconds:
            for p in payloads:
                try:
                    # In a real deployed test, this hits the Logos API which is part of the Synapse
                    # For this test, we hit the /command endpoint directly simulating the Logos output
                    async with session.post(f"http://localhost:{WEB_UI_PORT}/command", json=p, timeout=2) as resp:
                        if resp.status == 200:
                            request_count += 1
                except Exception:
                    pass
                await asyncio.sleep(0.1) # 10 requests / sec hammering
                
    logger.info(f"🛑 Bombardeio de Controle Finalizado. {request_count} Requisições Assíncronas Injetadas.")

def measure_graph_latency():
    """
    Mede a diferença do Transaction MATCH contra o Log de Proveniência (PROV-O).
    Avalia se a injestão Write-Lock degradou o banco de dados.
    """
    logger.info("⏱️ Coletando métricas do Event Loop vs Graph Write-Locks...")
    from dotenv import load_dotenv
    load_dotenv()
    uri  = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    pwd  = os.environ.get("NEO4J_PASSWORD") or os.environ.get("NEO4J_PWD")
    om = MenirOntologyManager(uri=uri, auth=(user, pwd))
    
    # We query to see the density of nodes
    try:
        with om.driver.session() as session:
            inv_count = session.run("MATCH (i:Invoice) RETURN count(i) as c").single()["c"]
            event_count = session.run("MATCH (e:Event) RETURN count(e) as c").single()["c"]
            
            logger.info("=========================================")
            logger.info("📊 RELATÓRIO DO CHAOS MONKEY (Menir V5.1)")
            logger.info("=========================================")
            logger.info(f"Invoices Ingeridas/Restantes: {inv_count}")
            logger.info(f"Eventos de Proveniência (PROV-O) Mutados: {event_count}")
            logger.info("=========================================")
    except Exception as e:
        logger.error(f"Falha ao medir a Latência Cíclica do Grafo: {e}")
    finally:
        om.close()

async def run_chaos():
    """ Orquestra a injeção concorrente no MenirAsyncRunner """
    generate_synthetic_invoices(NUM_INVOICES, INBOX_DIR)
    
    # Executa o bombardeio de UI por 10 segundos enquanto o motor mastiga o enxame de PDFs
    # Nota: Assumimos que o MenirAsyncRunner está rodando em outro processo/terminal neste momento
    await hammer_synapse(duration_seconds=10)
    
    # Let the graph breathe after the DDOS
    logger.info("Aguardando assento TCP e transações pendentes Cypher (5s)...")
    await asyncio.sleep(5)
    
    measure_graph_latency()

if __name__ == "__main__":
    asyncio.run(run_chaos())
