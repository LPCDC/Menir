from __future__ import annotations

import datetime as dt
import hashlib
import importlib
import importlib.util
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List

from urllib import request as urllib_request
from urllib.error import HTTPError, URLError


ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / ".env"
LOG = ROOT / "logs" / "operations.jsonl"
CHECKPOINT = ROOT / "artifacts" / "itau" / "checkpoint.md"

CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
LOG.parent.mkdir(parents=True, exist_ok=True)

ENV_TEMPLATE = """# Generated automatically by scripts/boot_now.py
# Populate with the credentials of your Menir environment when available.
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=changeme
"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd: str, cwd: Path = ROOT) -> str:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def _load_requests():
    spec = importlib.util.find_spec("requests")
    if spec is None:
        return None
    return importlib.import_module("requests")


def notify_grok(payload: dict) -> Dict[str, str]:
    url = os.getenv("GROK_WEBHOOK_URL", "http://localhost:5000/mcp/tool")
    token = os.getenv("GROK_TOKEN", "menir-local-token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    requests_mod = _load_requests()

    if requests_mod is not None:
        try:
            response = requests_mod.post(url, headers=headers, json=payload, timeout=10)
            return {"status": response.status_code, "text": response.text[:200]}
        except Exception as exc:  # pragma: no cover - defensive
            return {"status": "error", "text": str(exc)}

    data = json.dumps(payload).encode("utf-8")
    request = urllib_request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib_request.urlopen(request, timeout=10) as response:
            chunk = response.read(200)
            text = chunk.decode("utf-8", errors="replace")
            return {"status": response.status, "text": text}
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:  # pragma: no cover - defensive
        return {"status": "error", "text": str(exc)}


def detect_boot_trigger(user_input: str) -> bool:
    if not user_input:
        return False

    normalized = "".join(ch.lower() for ch in user_input if not ch.isspace())
    triggers = {
        "bootnow",
        "boot",
        "boot!",
        "nootnow",
        "boornow",
    }
    return normalized in triggers


def ensure_env() -> bool:
    if ENV.exists():
        return False
    ENV.write_text(ENV_TEMPLATE, encoding="utf-8")
    return True


def append_log(entry: dict) -> None:
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def perform_healthchecks() -> List[Dict[str, str]]:
    checks: List[Dict[str, str]] = []

    try:
        output = run("python --version")
        checks.append({"check": "python --version", "status": "ok", "output": output})
    except Exception as exc:  # pragma: no cover - defensive
        checks.append({"check": "python --version", "status": "error", "output": str(exc)})

    for relative in ("artifacts", "neo4j", "projects"):
        path = ROOT / relative
        check_name = f"ls {relative}"
        try:
            if path.exists():
                contents = " ".join(sorted(child.name for child in path.iterdir())) or "<empty>"
                checks.append({"check": check_name, "status": "ok", "output": contents})
            else:
                checks.append({"check": check_name, "status": "skipped", "output": "directory missing"})
        except Exception as exc:  # pragma: no cover - defensive
            checks.append({"check": check_name, "status": "error", "output": str(exc)})

    try:
        importlib.import_module("requests")
        checks.append({"check": "import requests", "status": "ok", "output": "available"})
    except Exception as exc:  # pragma: no cover - defensive
        checks.append({"check": "import requests", "status": "skipped", "output": str(exc)})

    return checks


def main() -> None:
    ts = dt.datetime.now(dt.timezone.utc).isoformat()
    env_created = ensure_env()

    if not CHECKPOINT.exists():
        CHECKPOINT.write_text("# checkpoint\n", encoding="utf-8")

    health = perform_healthchecks()

    entry = {
        "ts": ts,
        "action": "boot_now",
        "hash": sha256(CHECKPOINT),
        "env_created": env_created,
        "health": health,
    }

    append_log(entry)

    try:
        notify_status = notify_grok(entry)
    except Exception as exc:  # pragma: no cover - defensive
        notify_status = {"status": "error", "text": str(exc)}

    output = {**entry, "notify": notify_status}
    print(json.dumps(output))


if __name__ == "__main__":
    main()
