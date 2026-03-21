import asyncio
import aiohttp
import pytest
import jwt
import os
import json
from dotenv import load_dotenv

load_dotenv()

URL = "http://localhost:8080/api/v3/events/companion"
JWT_SECRET = os.getenv("MENIR_JWT_SECRET", "menir_secret_key_fixed")

def gen_token(tenant_id):
    return jwt.encode({"tenant_id": tenant_id, "exp": 9999999999}, JWT_SECRET, algorithm="HS256")

@pytest.mark.asyncio
async def test_sse_auth_rejection():
    """Verifica que o endpoint SSE rejeita conexões sem token ou com token inválido."""
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as resp:
            assert resp.status == 401

@pytest.mark.asyncio
async def test_sse_stream_open():
    """Verifica que o stream SSE abre com sucesso para um token válido."""
    token = gen_token("BECO")
    headers = {"Authorization": f"Bearer {token}"}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(URL, headers=headers) as resp:
                assert resp.status == 200
                assert resp.content_type == "text/event-stream"
                # Lendo apenas a primeira linha/evento para confirmar que está aberto
                async for line in resp.content:
                    if line:
                        decoded = line.decode('utf-8')
                        if decoded.startswith("data:"):
                            data = json.loads(decoded.replace("data: ", ""))
                            assert data["event"] == "connected"
                            assert data["tenant"] == "BECO"
                            break
                # Cancela após o primeiro evento para não ficar preso
        except asyncio.TimeoutError:
            pytest.fail("Timeout ao abrir stream SSE")
