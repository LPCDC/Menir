import asyncio
import os
from dotenv import load_dotenv
from src.v3.meta_cognition import MenirOntologyManager
from src.v3.menir_intel import MenirIntel
from src.v3.core.menir_runner import MenirAsyncRunner

async def main():
    load_dotenv(override=True)
    ontology = MenirOntologyManager()
    intel = MenirIntel(ontology=ontology)
    runner = MenirAsyncRunner(intel=intel, ontology_manager=ontology)
    
    # MenirAsyncRunner handles Synapse instantiation
    # but we need to start it.
    await runner.synapse.start_servers(http_port=8080)
    print("🚀 Synapse Test Server started on port 8080")
    
    # Stay alive
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
