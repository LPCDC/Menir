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
        invoices = list(session.run("MATCH (n:Invoice:BECO) RETURN n.invoice_number as num, n.date as dt, n.total_amount as amt"))
        transactions = list(session.run("MATCH (n:Transaction:BECO) WHERE n.amount > 0 RETURN n.debtor_name as debtor, n.booking_date as dt, n.amount as amt"))
        
        print(f"Total Invoices: {len(invoices)}")
        print(f"Total Transactions: {len(transactions)}")
        
        for inv in invoices:
            for tx in transactions:
                # Log de tentativa de match para "My Cafe Bar" ou valores similares
                if tx['amt'] == inv['amt'] or (inv['amt'] and abs(tx['amt'] - inv['amt']) < 0.1):
                    print(f"\nPOSSIBLE MATCH FOUND BY AMOUNT:")
                    print(f"  INV: {inv['num']} | Date: {inv['dt']} | Amt: {inv['amt']} (Type: {type(inv['amt'])})")
                    print(f"  TX:  {tx['debtor']} | Date: {tx['dt']} | Amt: {tx['amt']} (Type: {type(tx['amt'])})")
                    
                    # Checar Mes/Ano
                    # tr dt: 2026-01-05
                    # inv dt: 27.01.2026
                    tx_m = tx['dt'][5:7] if tx['dt'] else ""
                    tx_y = tx['dt'][0:4] if tx['dt'] else ""
                    inv_m = inv['dt'][3:5] if inv['dt'] else ""
                    inv_y = inv['dt'][6:10] if inv['dt'] else ""
                    
                    print(f"  MATCH MONTH: {tx_m} == {inv_m} -> {tx_m == inv_m}")
                    print(f"  MATCH YEAR:  {tx_y} == {inv_y} -> {tx_y == inv_y}")

if __name__ == "__main__":
    asyncio.run(debug())
