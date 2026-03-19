import os
import sys
import asyncio
from src.v3.meta_cognition import MenirOntologyManager
from src.v3.core.schemas.identity import TenantContext

sys.path.append(os.getcwd())

async def debug():
    TenantContext.set("BECO")
    ontology = MenirOntologyManager()
    
    with ontology.driver.session() as session:
        print("--- ALL BECO INVOICES ---")
        invs = list(session.run("MATCH (n:Invoice:BECO) RETURN n.invoice_number as num, n.client_name as client, n.total_amount as amt, n.status as st"))
        for r in invs:
            print(f"Num: {r['num']}, Client: '{r['client']}', Amt: {r['amt']}, Status: {r['st']}")
            
        print("\n--- ALL BECO TRANSACTIONS (CRDT) ---")
        txs = list(session.run("MATCH (n:Transaction:BECO) WHERE n.amount > 0 RETURN n.debtor_name as debtor, n.amount as amt"))
        for r in txs:
            print(f"Debtor: '{r['debtor']}', Amt: {r['amt']}")

if __name__ == "__main__":
    asyncio.run(debug())
