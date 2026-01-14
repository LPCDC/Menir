#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalization tool: WhatsApp TXT export → JSONL

Normaliza exportação TXT de WhatsApp → JSONL

Entrada: arquivos de texto exportados (uma ou múltiplas conversas)
Saída: JSONL com uma linha por mensagem

Campos por mensagem:
- message_id
- chat_id (nome/identificador da conversa)
- datetime (ISO 8601)
- author (nome ou número)
- text (conteúdo da mensagem)
- project_id
- tags (lista)

Usage:
  python3 tools/whatsapp_txt_to_jsonl.py --input data/itau/whatsapp/raw --output data/itau/whatsapp/normalized/whatsapp_messages.jsonl
"""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime
import re


def parse_args():
    p = argparse.ArgumentParser(description="WhatsApp TXT → JSONL")
    p.add_argument("--input", required=True, help="Diretório ou arquivo txt exportado WhatsApp")
    p.add_argument("--output", required=True, help="Arquivo JSONL de saída")
    return p.parse_args()


def parse_line(line, line_num=0):
    """
    Parsa linha do WhatsApp exportado.
    
    Padrão esperado: "[dd/mm/aaaa, hh:mm:ss] Nome: mensagem"
    Adaptar conforme export do seu WhatsApp.
    """
    try:
        if not line.strip() or not line.startswith("["):
            return None, None, None

        # Find closing bracket
        close = line.find("]")
        if close < 0:
            return None, None, None

        meta = line[1:close]
        rest = line[close + 2:] if close + 2 < len(line) else ""

        # Parse datetime
        parts = meta.split(", ")
        if len(parts) != 2:
            return None, None, None

        date_str, time_str = parts
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M:%S")
            iso = dt.isoformat()
        except ValueError:
            return None, None, None

        # Parse author and message
        if ": " in rest:
            author, msg = rest.split(": ", 1)
        else:
            author = None
            msg = rest

        return iso, author, msg.strip()

    except Exception:
        return None, None, None


def classify_message(text):
    """Classifica mensagem por tema."""
    txt = text.lower() if text else ""
    tags = []

    if "seguro" in txt or "venda casada" in txt:
        tags.append("POTENCIAL_VENDA_CASADA")
    if "imóvel" in txt or "garantia" in txt or "cgi" in txt:
        tags.append("CREDITO_IMOBILIARIO")
    if "ok" in txt or "tudo bem" in txt or "confirmo" in txt:
        tags.append("CONFIRMACAO")
    if "limite" in txt or "redução" in txt or "ajuste" in txt:
        tags.append("LIMIT_NEGOCIACAO")
    if "??" in txt or "?" in txt[-3:]:
        tags.append("PERGUNTA")
    if "reclamação" in txt or "problema" in txt or "erro" in txt:
        tags.append("RECLAMACAO")
    if "promete" in txt or "promessa" in txt or "vai" in txt:
        tags.append("PROMESSA")

    return tags if tags else ["OUTROS"]


def main():
    args = parse_args()

    input_path = Path(args.input)
    txt_files = []

    if input_path.is_dir():
        txt_files = list(input_path.glob("*.txt"))
    else:
        if input_path.exists():
            txt_files = [input_path]

    if not txt_files:
        print(f"⚠ No .txt files found in {args.input}")
        return

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    errors = 0
    msg_counter = 0

    with open(args.output, "w", encoding="utf-8") as out_f:
        for txt_file in txt_files:
            print(f"[*] Processing {txt_file}...")
            chat_id = txt_file.stem  # filename without extension

            try:
                with open(txt_file, encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        iso, author, text = parse_line(line, line_num)

                        if not iso or not text:
                            continue

                        try:
                            msg_id = f"wh_{msg_counter}"
                            msg_counter += 1

                            doc = {
                                "message_id": msg_id,
                                "chat_id": chat_id,
                                "datetime": iso,
                                "author": author,
                                "text": text,
                                "project_id": "PROJECT_ITAU_15220012",
                                "tags": classify_message(text)
                            }

                            out_f.write(json.dumps(doc, ensure_ascii=False) + "\n")
                            total += 1

                        except Exception as e:
                            errors += 1
                            print(f"  ⚠ Error processing line {line_num}: {e}")
                            continue

            except Exception as e:
                print(f"  ✗ Error opening {txt_file}: {e}")
                continue

    print(f"\n✅ Processed {total} messages ({errors} errors)")
    print(f"   Output: {args.output}")


if __name__ == "__main__":
    main()
