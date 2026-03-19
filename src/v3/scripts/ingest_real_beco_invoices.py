import os
import asyncio
import logging
import sys
import uuid
from decimal import Decimal

# Incluir diretorio raiz no path
sys.path.append(os.getcwd())

from src.v3.skills.excel_parser import BecoExcelParser
from src.v3.core.schemas.identity import TenantContext
from src.v3.meta_cognition import MenirOntologyManager
from src.v3.core.persistence import NodePersistenceOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BecoIngestion")

async def run_ingestion():
    TenantContext.set("BECO")
    parser = BecoExcelParser()
    data_dir = "tests/fixtures/real"
    excel_files = [f for f in os.listdir(data_dir) if f.endswith(".xlsx")]
    
    invoices_data = []
    invoice_numbers = {}

    print(f"--- FASE 1: PARSING E DUPLICATE CHECK ---")
    for filename in excel_files:
        path = os.path.join(data_dir, filename)
        try:
            data = parser.parse(path)
            inv_num = data["invoice_number"]
            
            if inv_num in invoice_numbers:
                print(f"⚠️ AVISO: Fatura duplicada {inv_num} em {filename} e {invoice_numbers[inv_num]}")
                data["status"] = "QUARANTINE"
                data["quarantine_reason"] = f"Invoice number collision with {invoice_numbers[inv_num]}"
            else:
                invoice_numbers[inv_num] = filename
                data["status"] = "PRODUCTION"
            
            invoices_data.append(data)
        except Exception as e:
            logger.error(f"Erro ao processar {filename}: {e}")

    print(f"\n--- FASE 2: PERSISTENCIA NO GRAFO (BECO) ---")
    ontology = MenirOntologyManager()
    
    with ontology.driver.session() as session:
        for inv in invoices_data:
            print(f"Persistindo: {inv['client_name']} | Doc: {inv['invoice_number']} | Status: {inv['status']}")
            
            # 1. MERGE Client
            session.run("""
                MERGE (c:Client:BECO {name: $name})
                SET c.address = $address,
                    c.project = 'BECO'
            """, name=inv["client_name"], address=inv["client_address"])
            
            # 2. MERGE Invoice ou QuarantineItem
            label = "Invoice" if inv["status"] == "PRODUCTION" else "QuarantineItem"
            # No caso de QuarantineItem, adicionar o motivo
            reason_set = "i.quarantine_reason = $reason," if inv["status"] == "QUARANTINE" else ""
            
            cypher = f"""
                MERGE (i:{label}:BECO {{invoice_number: $num}})
                SET i.date = $date,
                    i.referential_date = $ref_date,
                    i.total_amount = $total,
                    i.currency = $currency,
                    i.source_file = $source,
                    i.project = 'BECO',
                    i.ingested_at = datetime(),
                    {reason_set}
                    i.uid = coalesce(i.uid, $uid)
                WITH i
                MATCH (c:Client:BECO {{name: $name}})
                MERGE (c)-[:ORDERED]->(i)
                RETURN i
            """
            session.run(cypher, 
                num=inv["invoice_number"], 
                date=inv["invoice_date"],
                ref_date=inv["referential_date"],
                total=inv["total_amount"],
                currency=inv["currency"],
                source=inv["source_file"],
                uid=str(uuid.uuid4()),
                name=inv["client_name"],
                reason=inv.get("quarantine_reason", "")
            )
            
    print("\n✅ Ingestao concluida com sucesso.")

if __name__ == "__main__":
    asyncio.run(run_ingestion())
