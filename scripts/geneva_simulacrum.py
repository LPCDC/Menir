"""
Menir Core V5.1 - The Geneva Simulacrum
An End-to-End Architecture Test.
Injects a fake Temporal Rule into the Neo4j memory (5.3% TVA for My Cafe Bar),
then processes a synthetic invoice, reconciling it against a mocked bank transaction
and finally exporting the exact tabular data demanded by the Swiss Crésus ERP.
"""
import asyncio
import logging
import os
from datetime import datetime
from src.v3.meta_cognition import MenirOntologyManager
from src.v3.skills.invoice_skill import InvoiceSkill, InvoiceData, InvoiceLineItem
from src.v3.core.reconciliation import ReconciliationEngine
from src.v3.core.cresus_exporter import CresusExporter

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("GenevaSimulacrum")

async def run_simulacrum():
    tenant = "BECO"
    om = MenirOntologyManager()
    
    logger.info("=========================================")
    logger.info("🇨🇭 INICIANDO O SIMULACRO DE GENEBRA (V5.1)")
    logger.info("=========================================")

    # 1. INJETAR A ALUCINAÇÃO MÁGICA: A REGRA TDFN ESCONDIDA (5.3%)
    logger.info("💉 1. Injetando Regra Temporal TDFN Especial (5.3%) no Neo4j...")
    rule_query = f"""
    MERGE (t:Tenant {{name: '{tenant}'}})
    MERGE (r:TaxRule {{tenant_id: '{tenant}', type: 'TVA', rate: 5.3, valid_from: date('2020-01-01')}})
    MERGE (t)-[:HAS_TAX_RULE]->(r)
    """
    with om.driver.session() as session:
        session.run(rule_query)
        # Apagar resquícios de testes antigos do Cafe Bar para manter a idempontência limpa da Demo
        session.run("MATCH (v:Vendor {name: 'My Cafe Bar Sàrl'}) DETACH DELETE v")
        session.run(f"MATCH (i:Invoice:`{tenant}` {{file_hash: 'SIMULACRUM_HASH_001'}}) DETACH DELETE i")
        session.run(f"MATCH (tr:Transaction:`{tenant}` {{bank_ref: 'BANK_SIM_001'}}) DETACH DELETE tr")

    # 2. SIMULAR A EXTRAÇÃO PYDANTIC DA INVOICE SKILL (Com a Injeção de Contexto)
    logger.info("🧠 2. Construindo a Fatura Mental via Pydantic (Testando Validator Dinâmico)...")
    
    # O Dispatcher faria cache na memória:
    active_rules = om.get_tenant_active_context(tenant, "2026-02-15")
    valid_rates = active_rules.get('tva_rates', [8.1, 2.6])
    logger.info(f"O Córtex está ciente das Leis Atuais deste Tenant: {valid_rates}%")
    
    # Simula o output json cru do Gemini Flash que a Skill receberia
    raw_llm_json = {
        "vendor_name": "My Cafe Bar Sàrl",
        "vendor_iban": "CH9300000000000000000",
        "currency": "CHF",
        "issue_date": "2026-02-15",
        "subtotal": 21.0,
        "tip_or_unregulated_amount": 0.0,
        "total_amount": 22.11,
        "items": [
            {"description": "Latte Macchiato", "gross_amount": 10.50, "tva_rate_applied": 5.3},
            {"description": "Croissant", "gross_amount": 10.50, "tva_rate_applied": 5.3}
        ],
        "requires_manual_justification": True
    }
    
    # A MÁGICA DO VALIDADOR: Se tentar validar isso sem Contexto, vai expurgar o 5.3%
    # Passando { "valid_tva_rates": valid_rates } via `context`, a Skill aceita.
    try:
        validated_invoice = InvoiceData.model_validate(raw_llm_json, context={"valid_tva_rates": valid_rates})
        logger.info("✅ Pydantic Validou o Imposto Customizado via Grafo de Memória Temporal!")
    except Exception as e:
        logger.error(f"❌ Pydantic Rejeitou as Leis: {e}")
        return

    # 3. INJETAR A FATURA NO GRAFO (Roleplay da InvoiceSkill)
    logger.info("🗄️ 3. Injetando Fatura Auditada no Neo4j...")
    skill = InvoiceSkill(intel=None, ontology_manager=om)
    # Protegido por ID_Hash para poder emular sem chamar PDFs reais
    skill._inject_into_graph(validated_invoice, tenant, "SIMULACRUM_HASH_001")

    # 4. SIMULAR A TRANSAÇÃO BANCÁRIA ISO20022/CAMT053 (O Nó Banco)
    logger.info("🏦 4. Emulando a Chegada de um Extrato Bancário CAMT.053 correspondente...")
    camt_query = f"""
    MERGE (t:Tenant {{name: '{tenant}'}})
    MERGE (ba:BankAccount {{iban: 'CH00_TENANT_MAIN_ACCOUNT'}})
    MERGE (t)-[:OWNS_ACCOUNT]->(ba)
    MERGE (tr:Transaction:`{tenant}` {{bank_ref: 'BANK_SIM_001'}})
    SET tr.booking_date = '2026-02-16',
        tr.amount = -22.11, // Saída
        tr.currency = 'CHF',
        tr.debtor_name = 'My Cafe Bar Sàrl',
        tr.debtor_iban = 'CH9300000000000000000'
    MERGE (ba)-[:HAS_TRANSACTION]->(tr)
    """
    with om.driver.session() as session:
        session.run(camt_query)

    # 5. TESTE DE FOGO: A MÁQUINA DE RECONCILIAÇÃO HÍBRIDA
    logger.info("⚖️ 5. Despertando The Reconciliation Engine...")
    reconciliation = ReconciliationEngine(om)
    # Force the Tier 1 Exact Match to catch it
    reconciliation.run_matching_cycle(tenant)
    
    # Check what happened 
    with om.driver.session() as session:
        check = session.run(f"MATCH (i:Invoice {{file_hash:'SIMULACRUM_HASH_001'}})-[r:RECONCILED]->(tr) RETURN r.method AS method").single()
        if check:
            logger.info(f"✅ O Motor Reconciliou a Fatura com o Banco automaticamente via: {check['method']}")
        else:
            logger.error("❌ A Reconciliação Falhou. O Vértice não uniu a Fatura ao Banco.")
            return

    # 6. O PONTO FINAL: SÍNTESE CRÉSUS EXPORTER
    logger.info("📠 6. Iniciando a Geração de Matriz Crésus (Legado TXT)...")
    exporter = CresusExporter(om)
    # A exportação usará as contas de rascunho 1020 e 3400 e a formatação exigida
    filepath = await exporter.export_reconciled(tenant, export_dir="Menir_Cresus_Simulacrum")
    
    if filepath and os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            logger.info("=========================================")
            logger.info("📜 CRÉSUS PREVIEW DUMP:")
            logger.info(content)
            logger.info("=========================================")
            if "5.3" not in content and "22.11" in content:
                 logger.info("✅ Missão Cumprida. Valor líquido da matemática do TDFN foi validado, extraído, cruzado e empacotado para o Contador na sintaxe cega do Software.")

if __name__ == "__main__":
    asyncio.run(run_simulacrum())
