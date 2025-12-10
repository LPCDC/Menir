import uvicorn
import os
import json
import secrets
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Body, Security, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env na raiz (se existir)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Configuração de Logs
LOG_PATH = os.path.join(BASE_DIR, 'logs', 'operations.jsonl')
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# Logger configurado para stderr (console)
logger = logging.getLogger("menir_mcp")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI(title="Menir MCP Server", version="1.1.1")
security = HTTPBearer()

# Configuração de Modo e Token
MENIR_MODE = os.getenv("MENIR_MODE", "lab").lower()
MENIR_TOKEN = os.getenv("MENIR_MCP_TOKEN")
MENIR_VERSION = "v1.1.1"

logger.info(f"🔒 Menir Server starting in [{MENIR_MODE.upper()}] mode")

# Fail-safe startup for PROD
if MENIR_MODE == "prod" and not MENIR_TOKEN:
    logger.critical("❌ FATAL: MODE=PROD but MENIR_MCP_TOKEN is missing.")
    exit(1)

if MENIR_MODE == "lab" and not MENIR_TOKEN:
    logger.warning("⚠️  WARNING: Running in LAB mode without token. Use only for testing.")

def append_log(action: str, payload: dict, level: str = "INFO"):
    """Escreve no log oficial operations.jsonl"""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "action": action,
        "level": level,
        **payload
    }
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
    except Exception as e:
        logger.error(f"Failed to write to operations.jsonl: {e}")

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    # Se não tem token configurado e está em LAB, passa livre
    if not MENIR_TOKEN and MENIR_MODE == "lab":
        return None

    if not MENIR_TOKEN:
         raise HTTPException(status_code=500, detail="Server misconfigured: No Auth Token available")
        
    if not secrets.compare_digest(credentials.credentials, MENIR_TOKEN):
        # Log de falha de segurança
        logger.warning(f"⛔ Auth failed. Invalid token attempted.")
        append_log("auth_failure", {"error": "Invalid token"}, level="WARN")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

@app.get("/health")
async def health_check():
    """Retorna estado do servidor e status de segurança."""
    is_secured = bool(MENIR_TOKEN) or (MENIR_MODE == "prod")
    return {
        "status": "online",
        "mode": MENIR_MODE.upper(),
        "auth_secured": is_secured,
        "version": MENIR_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post('/chat')
async def chat(payload: dict = Body(...), token: str = Security(verify_token)):
    query = payload.get('query', '').lower()

    if 'eve' in query:
        append_log("ping", {"response": "Menir alive"})
        return {'response': 'Menir alive'}

    return {'response': "I'm Eve. Say 'eve' to wake me."}

if __name__ == '__main__':
    # Em PROD, idealmente bindaríamos em 127.0.0.1 ou usaríamos o token para proteger 0.0.0.0
    uvicorn.run(app, host="0.0.0.0", port=5000)
