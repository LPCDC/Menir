#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalization tool: MBOX de e-mails Itaú → JSONL

Entrada: arquivos .mbox no diretório raw
Saída: arquivo JSONL com um objeto por e-mail

Campos mínimos para cada email:
- message_id
- date (ISO 8601 UTC)
- from_email
- to_emails
- cc_emails
- subject
- body_text (plain text)
- project_id (fixo: PROJECT_ITAU_15220012)
- tags: list (tentativas de classificação)

Usage:
  python3 tools/itau_email_to_jsonl.py --input data/itau/email/raw --output data/itau/email/normalized/itau_emails.jsonl
"""

import mailbox
import json
import argparse
import glob
from datetime import datetime, timezone
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="Normalize Itaú MBOX → JSONL")
    p.add_argument("--input", required=True, help="Path glob ou diretório com .mbox files")
    p.add_argument("--output", required=True, help="Arquivo JSONL de saída")
    return p.parse_args()


def classify_email(subject, body):
    """Classifica email por tema baseado em subject e body."""
    tags = []
    subj = subject.lower() if subject else ""
    body_lower = body.lower() if body else ""

    if "seguro" in subj or "seguro" in body_lower:
        tags.append("SEGURO")
    if "crédito imobiliário" in subj or "cgi" in subj or "proposta" in subj:
        tags.append("CREDITO_IMOBILIARIO")
    if "limite" in subj or "redução" in subj or "ajuste de limite" in body_lower:
        tags.append("REDUCAO_LIMITE")
    if "crediário" in subj or "financiamento" in subj or "parcela" in subj:
        tags.append("CREDIARIO")
    if "atendimento" in subj or "cliente" in subj:
        tags.append("ATENDIMENTO")

    return tags if tags else ["OUTROS"]


def extract_body(message):
    """Extrai corpo da mensagem, priorizando text/plain."""
    if message.is_multipart():
        for part in message.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                try:
                    charset = part.get_content_charset() or "utf-8"
                    return part.get_payload(decode=True).decode(charset, errors="ignore")
                except Exception:
                    continue
    else:
        try:
            charset = message.get_content_charset() or "utf-8"
            return message.get_payload(decode=True).decode(charset, errors="ignore")
        except Exception:
            return None

    return None


def main():
    args = parse_args()

    # Resolve input path
    input_path = Path(args.input)
    mbox_files = []

    if input_path.is_dir():
        mbox_files = list(input_path.glob("*.mbox"))
    else:
        # Treat as glob pattern
        mbox_files = glob.glob(args.input)

    if not mbox_files:
        print(f"⚠ No .mbox files found in {args.input}")
        return

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    errors = 0

    with open(args.output, "w", encoding="utf-8") as out_f:
        for mbox_file in mbox_files:
            print(f"[*] Processing {mbox_file}...")
            try:
                mbox = mailbox.mbox(str(mbox_file))

                for msg in mbox:
                    try:
                        msgid = msg.get("Message-ID", "").strip()
                        if not msgid:
                            msgid = f"unknown_{total}"

                        # Parse date
                        try:
                            timestamp = mbox.get_unixtime(msg)
                            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                        except Exception:
                            dt = datetime.now(timezone.utc)

                        iso_date = dt.isoformat()

                        from_email = msg.get("From", "").strip()
                        to = [e.strip() for e in msg.get_all("To", []) if e]
                        cc = [e.strip() for e in msg.get_all("Cc", []) if e]
                        subject = msg.get("Subject", "").strip()
                        body = extract_body(msg)

                        tags = classify_email(subject, body)

                        doc = {
                            "message_id": msgid,
                            "date": iso_date,
                            "from_email": from_email,
                            "to_emails": to,
                            "cc_emails": cc,
                            "subject": subject,
                            "body": body,
                            "project_id": "PROJECT_ITAU_15220012",
                            "tags": tags
                        }

                        out_f.write(json.dumps(doc, ensure_ascii=False) + "\n")
                        total += 1

                    except Exception as e:
                        errors += 1
                        print(f"  ⚠ Error processing message: {e}")
                        continue

            except Exception as e:
                print(f"  ✗ Error opening {mbox_file}: {e}")
                continue

    print(f"\n✅ Processed {total} emails ({errors} errors)")
    print(f"   Output: {args.output}")


if __name__ == "__main__":
    main()
