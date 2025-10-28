import argparse
import hashlib
import json
import os
from datetime import datetime, timezone

LOG_DIR = os.path.join(os.getcwd(), "logs")
LOG_PATH = os.path.join(LOG_DIR, "zk_audit.jsonl")

def sha256_hex(text: str) -> str:
    h = hashlib.sha256()
    h.update(text.encode("utf-8"))
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", required=True, help="descrição curta do que foi feito")
    parser.add_argument("--result", required=True, help="OK / ERR / WARN etc")
    parser.add_argument("--details", default="", help="qualquer contexto adicional")
    args = parser.parse_args()

    # timestamp UTC ISO 8601
    ts_utc = datetime.now(timezone.utc).isoformat()

    # payload base que vamos hashear
    payload_core = {
        "ts_utc": ts_utc,
        "action": args.action,
        "result": args.result,
        "details": args.details,
    }

    # hash criptográfico do payload core
    payload_hash = sha256_hex(json.dumps(payload_core, sort_keys=True))

    # linha final registrada
    record = {
        "ts_utc": ts_utc,
        "action": args.action,
        "result": args.result,
        "details": args.details,
        "sha256": payload_hash,
    }

    # garantir pasta logs
    os.makedirs(LOG_DIR, exist_ok=True)

    # append como JSONL
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # eco simples para uso humano / scripts
    print(json.dumps(record, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
