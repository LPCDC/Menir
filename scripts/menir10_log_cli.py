#!/usr/bin/env python
"""
menir10_log_cli.py – CLI mínimo para registrar interações no Menir-10.

Uso básico (no diretório do repositório):

    export MENIR_PROJECT_ID=tivoli
    python scripts/menir10_log_cli.py -c "Reunião com síndico sobre orçamento"

Ou, sem MENIR_PROJECT_ID:

    python scripts/menir10_log_cli.py --project itau_15220012 -c "Ligação com Tatiana sobre prazo do cartório"
"""

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
import os


def main() -> None:
    parser = argparse.ArgumentParser(description="Registrar uma interação no Menir-10 (JSONL).")
    parser.add_argument(
        "-c",
        "--content",
        required=True,
        help="Texto da interação (descrição do evento).",
    )
    parser.add_argument(
        "--project",
        "--project_id",
        dest="project_id",
        default=os.getenv("MENIR_PROJECT_ID", "default"),
        help="ID do projeto (ex.: tivoli, itau_15220012, ibere). "
             "Se omitido, usa MENIR_PROJECT_ID ou 'default'.",
    )
    parser.add_argument(
        "--role",
        default="user",
        help="Papel na interação (user/assistant/outro). Default: user.",
    )
    parser.add_argument(
        "--log-path",
        default="logs/menir10_interactions.jsonl",
        help="Caminho do arquivo de log JSONL. Default: logs/menir10_interactions.jsonl",
    )

    args = parser.parse_args()

    ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    interaction_id = uuid.uuid4().hex

    entry = {
        "interaction_id": interaction_id,
        "project_id": args.project_id,
        "role": args.role,
        "content": args.content,
        "ts": ts,
        "meta": {},
    }

    log_path = Path(args.log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"OK: gravado em {log_path} (interaction_id={interaction_id}, project_id={args.project_id})")


if __name__ == "__main__":
    main()
