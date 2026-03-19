import os
import sys
import asyncio
from src.v3.meta_cognition import MenirOntologyManager
from src.v3.core.schemas.identity import TenantContext

# Incluir diretorio raiz no path
sys.path.append(os.getcwd())

async def inspect():
    TenantContext.set("BECO")
    ontology = MenirOntologyManager()
    
    print("--- INSPECAO BECO HOJE (2026-03-19) ---")
    
    # Buscar Invoices
    query_inv = """
    MATCH (n:Invoice:BECO)
    WHERE n.ingested_at >= datetime('2026-03-19')
    RETURN n.invoice_number as num, n.date as dt, n.total_amount as amt, n.status as st, keys(n) as k
    """
    
    # Buscar Transactions
    query_tx = """
    MATCH (n:Transaction:BECO)
    WHERE n.ingested_at >= datetime('2026-03-19') AND n.amount > 0
    RETURN n.debtor_name as debtor, n.booking_date as dt, n.amount as amt
    """
    
    with ontology.driver.session() as session:
        print("\n[INVOICES]")
        res_inv = session.run(query_inv)
        for r in res_inv:
            print(f"Num: {r['num']}, Date: {r['dt']}, Amt: {r['amt']}, Status: {r['st']}, Keys: {r['k']}")
            
        print("\n[TRANSACTIONS]")
        res_tx = session.run(query_tx)
        for r in res_tx:
            print(f"Debtor: {r['debtor']}, Date: {r['dt']}, Amt: {r['amt']}")

if __name__ == "__main__":
    asyncio.run(inspect())
