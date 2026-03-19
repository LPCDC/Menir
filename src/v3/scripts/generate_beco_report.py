import os
import sys
import asyncio
import json
from src.v3.meta_cognition import MenirOntologyManager
from src.v3.core.schemas.identity import TenantContext

sys.path.append(os.getcwd())

async def generate_report():
    TenantContext.set("BECO")
    ontology = MenirOntologyManager()
    
    report = {
        "tenant": "BECO",
        "period": "January 2026",
        "invoices": {
            "total_issued": 0,
            "total_amount_billed": 0.0,
            "paid": [],
            "unpaid": [],
            "quarantined": []
        },
        "bank_reconciliation": {
            "reconciled_count": 0,
            "total_received": 0.0
        }
    }
    
    with ontology.driver.session() as session:
        # 1. Invoices (Excluindo quarentena por enquanto para o total billing)
        invoices = session.run("""
            MATCH (c:Client:BECO)-[:ORDERED]->(i:Invoice:BECO)
            OPTIONAL MATCH (tr:Transaction:BECO)-[r:RECONCILED]->(i)
            RETURN i.invoice_number as num, i.total_amount as amt, i.status as st, 
                   c.name as client, tr.tx_id as tx, r.method as method
        """)
        
        for r in invoices:
            inv_data = {
                "number": r['num'],
                "client": r['client'],
                "amount": r['amt'],
                "status": r['st']
            }
            report["invoices"]["total_issued"] += 1
            report["invoices"]["total_amount_billed"] += (r['amt'] or 0.0)
            
            if r['tx']:
                inv_data["reconciled_with"] = r['tx']
                inv_data["match_method"] = r['method']
                report["invoices"]["paid"].append(inv_data)
                report["bank_reconciliation"]["reconciled_count"] += 1
            else:
                report["invoices"]["unpaid"].append(inv_data)

        # 2. Quarantine Items
        quarantine = session.run("MATCH (q:QuarantineItem:BECO) RETURN q.invoice_number as num, q.quarantine_reason as reason")
        for r in quarantine:
            report["invoices"]["quarantined"].append({"num": r['num'], "reason": r['reason']})
            
    # Salvar Report
    report_path = "beco_january_2026_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
        
    print(f"--- RELATORIO FINANCEIRO GERADO: {report_path} ---")
    print(f"Total Billed: {report['invoices']['total_amount_billed']} CHF")
    print(f"Reconciled: {report['bank_reconciliation']['reconciled_count']} invoices")
    print(f"Unpaid: {len(report['invoices']['unpaid'])}")

if __name__ == "__main__":
    asyncio.run(generate_report())
