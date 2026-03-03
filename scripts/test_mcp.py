import asyncio
import aiohttp
import json

from src.v3.core.synapse import MenirSynapse

class DummyRunner:
    pass

async def test_mcp_galvanic_isolation():
    print("🚀 Booting Mock MenirSynapse Control Plane...")
    
    dummy_runner = DummyRunner()
    synapse = MenirSynapse(dummy_runner)
    
    # Inicia apenas o Gateway HTTP (Evitando o Raw Socket p/ evitar conflitos)
    from aiohttp import web
    runner_app = web.AppRunner(synapse.app)
    await runner_app.setup()
    site = web.TCPSite(runner_app, '127.0.0.1', 8080)
    await site.start()
    
    url = "http://127.0.0.1:8080/mcp"
    
    headers_beco = {"Authorization": "Bearer BECO_JWT"}
    headers_santos = {"Authorization": "Bearer SANTOS_LIFE_JWT"}
    headers_root = {"Authorization": "Bearer ROOT_ADMIN_JWT"}
    
    payload_list = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }

    async with aiohttp.ClientSession() as session:
        print("\n--- 🛡️ TESTING GALVANIC ISOLATION ---")
        
        # Test 1: BECO (Fiduciary)
        async with session.post(url, headers=headers_beco, json=payload_list) as resp:
            data = await resp.json()
            tools = [t["name"] for t in data.get("result", {}).get("tools", [])]
            print(f"BECO Tools Visible: {tools}")

        # Test 2: SANTOS (Standard User)
        async with session.post(url, headers=headers_santos, json=payload_list) as resp:
            data = await resp.json()
            tools = [t["name"] for t in data.get("result", {}).get("tools", [])]
            print(f"SANTOS Tools Visible: {tools}")

        # Test 3: ROOT (System Admin)
        async with session.post(url, headers=headers_root, json=payload_list) as resp:
            data = await resp.json()
            tools = [t["name"] for t in data.get("result", {}).get("tools", [])]
            print(f"ROOT Tools Visible: {tools}")
            
        print("\n--- 🛠️ TESTING TOOL EXECUTION (CHOKE-POINT) ---")
        
        payload_illegal_call = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "export_cresus_tabular",
                "arguments": {}
            },
            "id": 2
        }

        # Test 4: SANTOS trying to execute BECO's tool
        async with session.post(url, headers=headers_santos, json=payload_illegal_call) as resp:
            data = await resp.json()
            print(f"SANTOS calling 'export_cresus': {json.dumps(data)}")

        # Test 5: BECO successfully executing VAT tool (Mock)
        payload_legal_call = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "validate_swiss_vat",
                "arguments": {"vat_number": "CHE-123.456.789"}
            },
            "id": 3
        }
        async with session.post(url, headers=headers_beco, json=payload_legal_call) as resp:
            data = await resp.json()
            print(f"BECO calling 'validate_swiss_vat': {json.dumps(data)}")

    await runner_app.cleanup()
    print("\n✅ Test Concluded.")

if __name__ == "__main__":
    asyncio.run(test_mcp_galvanic_isolation())
