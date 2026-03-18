import asyncio
import json
import os
import jwt
from unittest.mock import AsyncMock, MagicMock, patch
from src.v3.core.synapse import MenirSynapse
from aiohttp import web

async def main():
    runner = MagicMock()
    runner.ontology_manager.driver.session = MagicMock()
    intel = MagicMock()
    
    synapse = MenirSynapse(runner, intel)
    
    jwt_secret = "super_secret_menir_key_2026_replaced"
    os.environ["MENIR_JWT_SECRET"] = jwt_secret
    token = jwt.encode({"tenant_id": "BECO"}, jwt_secret, algorithm="HS256")
    
    mock_request = MagicMock(spec=web.Request)
    mock_request.headers = {"Authorization": f"Bearer {token}"}
    
    mock_session = MagicMock()
    runner.ontology_manager.driver.session.return_value.__enter__.return_value = mock_session
    
    mock_record = MagicMock()
    mock_record.data.return_value = {"q": {"uid": "q-123", "status": "PENDING"}}
    mock_result = MagicMock()
    mock_result.all.return_value = [mock_record]
    mock_session.run.return_value = mock_result
    
    print("Testing handle_get_quarantine_documents...")
    try:
        response = await synapse.handle_get_quarantine_documents(mock_request)
        print(f"Status: {response.status}")
        print(f"Body: {response.text}")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
