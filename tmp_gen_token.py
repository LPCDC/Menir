import jwt
import os
import time
from dotenv import load_dotenv

load_dotenv()

secret = os.getenv("MENIR_JWT_SECRET")
if not secret:
    # Use a fallback if not set, but better to check .env
    secret = "test-secret"

payload = {
    "tenant_id": "BECO",
    "user_uid": "test-user-123", # Required by synapse.py
    "iat": int(time.time()),
    "exp": int(time.time()) + 3600
}

token = jwt.encode(payload, secret, algorithm="HS256")
print(f"GENERATED_TOKEN:{token}")
