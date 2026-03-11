import asyncio
from dotenv import load_dotenv
load_dotenv()

from src.v3.core.synapse import MenirSynapse
from src.v3.core.menir_runner import MenirAsyncRunner
from src.v3.meta_cognition import MenirOntologyManager
from src.v3.menir_intel import MenirIntel

async def start():
    # Load required core systems for synapse to boot
    intel = MenirIntel()
    ontology = MenirOntologyManager()
    runner = MenirAsyncRunner(intel, ontology)
    synapse = MenirSynapse(runner)
    
    # Start on 8000 so the frontend can reach it
    await synapse.start_servers(http_port=8000, socket_port=8081)
    
    # Keep alive
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    asyncio.run(start())
