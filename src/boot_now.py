from pathlib import Path
import subprocess, hashlib, json, os, datetime as dt

# Optional Menir-10 instrumentation
try:
    from menir10.menir10_boot import start_boot_interaction, complete_boot_interaction
except ImportError:
    start_boot_interaction = None
    complete_boot_interaction = None

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / '.env'
LOG = ROOT / 'logs' / 'operations.jsonl'
ART = ROOT / 'artifacts' / 'itau'
ART.mkdir(parents=True, exist_ok=True)
LOG.parent.mkdir(parents=True, exist_ok=True)

def sha256(p: Path): return hashlib.sha256(p.read_bytes()).hexdigest()

def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()

def notify_grok(payload: dict):
    import requests
    url = os.getenv('GROK_WEBHOOK_URL', 'http://localhost:5000/mcp/tool')
    tok = os.getenv('GROK_TOKEN', 'menir-local-token')
    headers = {'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json'}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        return {'status': resp.status_code, 'text': resp.text[:200]}
    except Exception as e:
        return {'status': 'error', 'text': str(e)}

def main():
    state = None
    if start_boot_interaction is not None:
        state = start_boot_interaction()
    
    try:
        ts = dt.datetime.now(dt.timezone.utc).isoformat()
        chk = ART / 'checkpoint.md'
        if not chk.exists(): chk.write_text('# checkpoint\n', encoding='utf-8')
        entry = {'ts': ts, 'action': 'boot_now', 'hash': sha256(chk)}
        LOG.write_text((LOG.read_text(encoding='utf-8') + '\n' if LOG.exists() else '') + json.dumps(entry), encoding='utf-8')
        note = notify_grok({'service': 'Menir', 'event': 'boot_now', 'ts': ts, 'hash': entry['hash']})
        print(json.dumps({'boot_now': 'OK', 'notify': note}))
        
        if state is not None and complete_boot_interaction is not None:
            complete_boot_interaction(state, status="ok")
    
    except Exception as e:
        if state is not None and complete_boot_interaction is not None:
            complete_boot_interaction(state, status="error", extra={"error": str(e)})
        raise

if __name__ == '__main__': main()

