#!/usr/bin/env python
"""
CLI mínimo para registrar interações Menir-10 em logs/menir10_interactions.jsonl.
"""

import argparse
import sys
from typing import Optional

from menir10.menir10_log import append_log, MissingProjectIdError


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Log de interações Menir-10 em JSONL."
    )
    parser.add_argument(
        "-p",
        "--project-id",
        help="ID do projeto (se omitido, usa MENIR_PROJECT_ID do ambiente).",
    )
    parser.add_argument(
        "-c",
        "--content",
        required=True,
        help="Conteúdo principal da interação (mensagem resumida).",
    )
    parser.add_argument(
        "--intent-profile",
        default="note",
        help="Perfil de intenção (ex.: boot, note, call, summary). Default: note.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    try:
        record = append_log(
            project_id=args.project_id,
            intent_profile=args.intent_profile,
            content=args.content,
        )
    except MissingProjectIdError as exc:
        sys.stderr.write(f"ERRO: {exc}\n")
        return 1
    except Exception as exc:
        sys.stderr.write(f"ERRO inesperado ao logar interação: {exc}\n")
        return 1

    pid = record["project_id"]
    iid = record["interaction_id"]
    print(f"OK: evento registrado para projeto '{pid}'. interaction_id={iid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env python
import argparse
import datetime as _dt
import json
import os
import pathlib
import sys
import uuid

def main() -> None:
    parser = argparse.ArgumentParser(
        description="CLI mínimo para registrar eventos no Menir-10 por projeto."
    )
    parser.add_argument(
        "-p",
        "--project",
        dest="project_id",
        help="ID do projeto (ex.: tivoli, itau_15220012). "
             "Se omitido, usa MENIR_PROJECT_ID.",
    )
    parser.add_argument(
        "-c",
        "--content",
        dest="content",
        required=True,
        help="Texto do evento / nota a ser registrada.",
    )
    args = parser.parse_args()

    project_id = args.project_id or os.getenv("MENIR_PROJECT_ID")
    if not project_id:
        print(
            "ERRO: informe --project ou defina MENIR_PROJECT_ID antes de usar o CLI.\n"
            "Exemplos:\n"
            "  export MENIR_PROJECT_ID=tivoli\n"
            "  python scripts/menir10_log_cli.py -c \"Reunião com síndico\"\n"
            "ou\n"
            "  python scripts/menir10_log_cli.py -p itau_15220012 -c \"Ligação com gerente\"",
            file=sys.stderr,
        )
        sys.exit(1)

    logs_dir = pathlib.Path("logs")
    logs_dir.mkdir(exist_ok=True)
    path = logs_dir / "menir10_interactions.jsonl"

    now = _dt.datetime.now(_dt.timezone.utc).isoformat()
    record = {
        "interaction_id": str(uuid.uuid4()),
        "project_id": project_id,
        "intent_profile": "note",
        "created_at": now,
        "updated_at": now,
        "flags": {},
        "metadata": {
            "stage": "single",
            "status": "ok",
            "source": "cli",
            "content": args.content,
        },
    }

    with path.open("a", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False)
        f.write("\n")

    print(f"OK: evento registrado em {path} para projeto '{project_id}'.")

if __name__ == "__main__":
    main()
