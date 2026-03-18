import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from src.v3.core.cresus_exporter import CresusExporter
from src.v3.meta_cognition import MenirOntologyManager

async def test_exporter():
    ontology_manager = MenirOntologyManager("BECO")
    exporter = CresusExporter(ontology_manager)
    filepath = await exporter.export_reconciled("BECO")
    if filepath and os.path.exists(filepath):
        print(f"\n--- INICIO ARQUIVO {filepath} ---")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                print(repr(content)) # Usar repr para ver as tabulações e \r\n
                print(content)
        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
        print("--- FIM ARQUIVO ---\n")
    else:
        print("Nenhum arquivo gerado (sem faturas reconciliadas?)")

if __name__ == "__main__":
    asyncio.run(test_exporter())
