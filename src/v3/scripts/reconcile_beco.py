import os
import asyncio
import sys
import logging
from decimal import Decimal

# Incluir diretorio raiz no path
sys.path.append(os.getcwd())

from src.v3.meta_cognition import MenirOntologyManager
from src.v3.core.schemas.identity import TenantContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BecoReconciliation")

async def run_reconciliation():
    TenantContext.set("BECO")
    ontology = MenirOntologyManager()
    
    print(f"--- INICIANDO RECONCILIACAO BANCARIA (BECO) ---")
    
    query = """
    MATCH (tr:Transaction:BECO)
    WHERE tr.amount > 0
    AND NOT (tr)-[:RECONCILED]->(:Invoice)
    
    MATCH (c:Client:BECO)-[:ORDERED]->(inv:Invoice:BECO)
    WHERE inv.status = 'PENDING' OR inv.status IS NULL
    
    // Match por Nome (Fuzzy - Case Insensitive)
    WITH tr, inv, c
    WHERE toLower(c.name) CONTAINS toLower(tr.debtor_name)
       OR toLower(tr.debtor_name) CONTAINS toLower(c.name)
       OR (tr.remittance_info IS NOT NULL AND toLower(tr.remittance_info) CONTAINS toLower(c.name))

    // Match por Valor (Tolerancia de 100 CHF)
    WITH tr, inv, c
    WHERE abs(tr.amount - inv.total_amount) < 100.0
    
    MERGE (tr)-[r:RECONCILED]->(inv)
    SET r.method = 'FUZZY_RELATION_MATCH',
        r.discrepancy = tr.amount - inv.total_amount,
        r.reconciled_at = datetime(),
        inv.status = 'PAID'
    RETURN tr.debtor_name as debtor, c.name as client, inv.invoice_number as inv_num, tr.amount as tx_amt, inv.total_amount as inv_amt
    """
    
    with ontology.driver.session() as session:
        result = session.run(query)
        reconciled_count = 0
        for record in result:
            print(f"✅ Reconciliado: {record['debtor']} -> Fatura {record['inv_num']} (Bancario: {record['tx_amt']} | Fatura: {record['inv_amt']})")
            reconciled_count += 1
            
    print(f"\n--- TOTAL RECONCILIADO: {reconciled_count} faturas ---")

if __name__ == "__main__":
    asyncio.run(run_reconciliation())
