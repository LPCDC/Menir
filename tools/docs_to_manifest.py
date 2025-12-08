#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalization tool: Document directory → manifest JSON

Cria um manifest JSON do conjunto de documentos avulsos (scans, PDFs de declaração, prints)

Entrada: diretório de docs
Saída: JSON com metadados: path, hash, tipo presumido

Usage:
  python3 tools/docs_to_manifest.py --input data/itau/docs --output data/itau/docs/itau_docs_manifest.json
"""

import os
import hashlib
import json
import argparse
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Docs dir → manifest JSON")
    parser.add_argument("--input", required=True, help="Diretório com documentos")
    parser.add_argument("--output", required=True, help="Arquivo JSON de manifest saída")
    return parser.parse_args()


def file_hash(path, algo='sha256'):
    """Calcula hash do arquivo."""
    h = hashlib.new(algo)
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        print(f"  ⚠ Could not hash {path}: {e}")
        return None


def classify_doc(path):
    """Classifica tipo de documento baseado no nome."""
    name = os.path.basename(path).lower()

    if "testemunha" in name or "carol" in name or "declaracao" in name:
        return "DECLARACAO_TESTEMUNHA"
    if "contrato" in name or "minuta" in name or "assinado" in name:
        return "CONTRATO"
    if "whatsapp" in name or "print_wh" in name or "chat" in name:
        return "TRECHO_WHATSAPP"
    if "extrato" in name or "banco" in name or "statement" in name:
        return "EXTRATO_BANCARIO"
    if "comprovante" in name or "recibo" in name or "receipt" in name:
        return "COMPROVANTE"
    if "declaração" in name or "ir" in name or "imposto" in name:
        return "DECLARACAO_IR"
    if "procuração" in name or "procuracao" in name:
        return "PROCURACAO"

    return "DOCUMENTO_GENERICO"


def main():
    args = parse_args()

    input_path = Path(args.input)

    if not input_path.is_dir():
        print(f"✗ Input path is not a directory: {args.input}")
        return

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = []
    total = 0
    errors = 0

    print(f"[*] Scanning {args.input}...")

    for root, dirs, files in os.walk(input_path):
        for fname in files:
            path = os.path.join(root, fname)
            try:
                file_hash_val = file_hash(path)

                if file_hash_val is None:
                    errors += 1
                    continue

                doc = {
                    "path": path,
                    "filename": fname,
                    "hash_sha256": file_hash_val,
                    "type": classify_doc(path),
                    "size_bytes": os.path.getsize(path)
                }

                manifest.append(doc)
                total += 1

            except Exception as e:
                errors += 1
                print(f"  ⚠ Error processing {fname}: {e}")
                continue

    # Write manifest
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Scanned {total} documents ({errors} errors)")
    print(f"   Output: {args.output}")

    # Print summary by type
    if manifest:
        type_counts = {}
        for doc in manifest:
            doc_type = doc.get("type", "UNKNOWN")
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1

        print("\n   Document types:")
        for doc_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"     - {doc_type}: {count}")


if __name__ == "__main__":
    main()
