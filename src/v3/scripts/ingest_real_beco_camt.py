import os
import asyncio
import sys
import logging

# Incluir diretorio raiz no path
sys.path.append(os.getcwd())

from src.v3.skills.camt053_skill import Camt053Skill
from src.v3.meta_cognition import MenirOntologyManager
from src.v3.core.schemas.identity import TenantContext

logging.basicConfig(level=logging.INFO)

async def run_camt_ingestion():
    TenantContext.set("BECO")
    ontology = MenirOntologyManager()
    skill = Camt053Skill(ontology)
    
    camt_file = "tests/fixtures/real/00788_CAMT053_CH3400788000050770303_20260225165007_841011619___.xml.old"
    
    print(f"--- INGESTAO CAMT053: {os.path.basename(camt_file)} ---")
    result = await skill.process_statement(camt_file, tenant="BECO")
    
    if result.success:
        print(f"✅ Sucesso: {result.message}")
    else:
        print(f"❌ Falha: {result.message}")

if __name__ == "__main__":
    asyncio.run(run_camt_ingestion())
