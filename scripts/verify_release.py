import os
import sys
import time
import requests
import subprocess
import signal

# Config
BASE_URL = "http://127.0.0.1:5000"
HEALTH_URL = f"{BASE_URL}/health"
CHAT_URL = f"{BASE_URL}/chat"
TOKEN = os.getenv("MENIR_MCP_TOKEN", "test-token")

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def run_server():
    log("Starting MCP Server...", "STEP")
    # Usa o proprio executavel python do ambiente
    cmd = [sys.executable, "scripts/mcp_server.py"]
    # Configura ambiente de teste se precisar
    env = os.environ.copy()
    if "MENIR_MCP_TOKEN" not in env:
        env["MENIR_MCP_TOKEN"] = TOKEN
        env["MENIR_MODE"] = "prod" # Forcar prod para testar auth
    
    # Inicia processo sem bloquear
    proc = subprocess.Popen(cmd, env=env)
    return proc

def wait_for_server():
    log("Waiting for server to be healthy...", "STEP")
    for _ in range(10):
        try:
            r = requests.get(HEALTH_URL, timeout=1)
            if r.status_code == 200:
                log("Server is UP!", "OK")
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    log("Server failed to start", "ERROR")
    return False

def check_health():
    log("Checking /health...", "STEP")
    r = requests.get(HEALTH_URL)
    data = r.json()
    if r.status_code == 200 and data.get("status") == "online":
        log(f"Health OK: {data}", "OK")
    else:
        log(f"Health Failed: {r.text}", "ERROR")
        sys.exit(1)

def check_auth():
    log("Checking Auth...", "STEP")
    
    # 1. Valid Token
    headers = {"Authorization": f"Bearer {TOKEN}"}
    r = requests.post(CHAT_URL, json={"query": "eve"}, headers=headers)
    if r.status_code == 200:
        log("Auth Valid Token: OK", "OK")
    else:
        log(f"Auth Valid Token Failed: {r.status_code}", "ERROR")
        sys.exit(1)
        
    # 2. Invalid Token
    bad_headers = {"Authorization": "Bearer BAD_TOKEN"}
    r = requests.post(CHAT_URL, json={"query": "eve"}, headers=bad_headers)
    if r.status_code == 401:
        log("Auth Invalid Token: OK (401 received)", "OK")
    else:
        log(f"Auth Invalid Token Verification Failed: got {r.status_code}, expected 401", "ERROR")
        sys.exit(1)

def check_backup():
    log("Running Backup Routine...", "STEP")
    ret = subprocess.call([sys.executable, "scripts/backup_routine.py"])
    if ret == 0:
        log("Backup script execution: OK", "OK")
    else:
        log("Backup script failed", "ERROR")
        sys.exit(1)
        
    # Check File existence
    if not os.path.exists("backups"):
        log("Backups dir missing", "ERROR")
        sys.exit(1)
    
    files = os.listdir("backups")
    if any(f.startswith("menir_backup_") for f in files):
         log(f"Backup file found. Count: {len(files)}", "OK")
    else:
         log("No backup zip found in backups/", "ERROR")
         sys.exit(1)

def main():
    print("=== MENIR RELEASE VERIFICATION (Python) ===\n")
    
    # Verificar se server ja esta rodando (evita conflito)
    try:
        requests.get(HEALTH_URL, timeout=1)
        log("Server appears to be running already. Using existing instance.", "WARN")
        proc = None
    except:
        proc = run_server()
        if not wait_for_server():
            if proc: proc.kill()
            sys.exit(1)

    try:
        check_health()
        check_auth()
        check_backup()
        log("ALL CHECKS PASSED ✅", "SUCCESS")
    finally:
        if proc:
            log("Stopping Server...", "STEP")
            proc.terminate()
            proc.wait()
            log("Server Stopped", "OK")

if __name__ == "__main__":
    main()
