#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalization tool: PDF extrato Itaú → JSONL

Extrai transações relevantes de PDF de extrato Itaú → JSONL

Entrada: PDFs no diretório raw
Saída: transações em JSONL

Campos por transação:
- transaction_id
- date (YYYY-MM-DD)
- description (texto bruto)
- amount (float; negativo para débito, positivo para crédito)
- balance_after (float, se disponível)
- project_id
- tags: list

Usage:
  python3 tools/itau_extrato_to_jsonl.py --input data/itau/extratos/raw --output data/itau/extratos/normalized/extratos.jsonl

TODO: Implementar PDF parsing real (pdfplumber, PyPDF2, ou camelot)
      Por enquanto, usa stub que retorna lista vazia.
"""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime
import re


def parse_args():
    p = argparse.ArgumentParser(description="PDF extrato Itaú → JSONL")
    p.add_argument("--input", required=True, help="Path ou diretório com PDFs")
    p.add_argument("--output", required=True, help="Arquivo JSONL de saída")
    return p.parse_args()


def extract_transactions_from_pdf(path_pdf):
    """
    TODO: Implementar parsing real de PDF para extrair:
    - data (YYYY-MM-DD)
    - descrição da transação
    - valor
    - saldo após transação

    Bibliotecas recomendadas:
    - pdfplumber: excelente para tabelas
    - PyPDF2: parsing básico
    - camelot: tabelas estruturadas

    Por enquanto, retorna lista vazia como stub.
    """
    transactions = []
    
    # TODO: Descomente e implemente quando PDF parser estiver disponível
    # try:
    #     import pdfplumber
    #     with pdfplumber.open(path_pdf) as pdf:
    #         for page in pdf.pages:
    #             tables = page.extract_tables()
    #             if tables:
    #                 for table in tables:
    #                     # Parse each row as transaction
    #                     for row in table[1:]:  # Skip header
    #                         if len(row) >= 3:
    #                             transactions.append({
    #                                 "date": row[0],
    #                                 "description": row[1],
    #                                 "amount": float(row[2].replace(",", ".")),
    #                                 "balance_after": float(row[3].replace(",", ".")) if len(row) > 3 else None,
    #                             })
    # except Exception as e:
    #     print(f"  ⚠ Could not parse PDF {path_pdf}: {e}")

    return transactions


def classify_transaction(description):
    """Classifica transação por tipo baseado na descrição."""
    desc = description.lower() if description else ""
    tags = []

    if "seguro" in desc:
        tags.append("DEBITO_SEGURO")
    if "crediário" in desc or "parcela" in desc or "financ" in desc:
        if "liber" in desc or "crédito" in desc or "desbloqu" in desc:
            tags.append("EMPRESTIMO_LIBERACAO")
        else:
            tags.append("PARCELA_CREDIARIO")
    if "cgi" in desc or "imobiliário" in desc or "imóvel" in desc:
        tags.append("CREDITO_IMOBILIARIO")
    if "pix" in desc or "ted" in desc or "transferência" in desc:
        tags.append("TRANSFERENCIA")
    if "compra" in desc or "débito" in desc:
        tags.append("COMPRA")

    return tags if tags else ["OUTROS"]


def main():
    args = parse_args()

    input_path = Path(args.input)
    pdf_files = []

    if input_path.is_dir():
        pdf_files = list(input_path.glob("*.pdf"))
    else:
        if input_path.exists():
            pdf_files = [input_path]

    if not pdf_files:
        print(f"⚠ No PDF files found in {args.input}")
        return

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    errors = 0
    tx_counter = 0

    with open(args.output, "w", encoding="utf-8") as out_f:
        for pdf_file in pdf_files:
            print(f"[*] Processing {pdf_file}...")
            try:
                transactions = extract_transactions_from_pdf(str(pdf_file))

                for t in transactions:
                    try:
                        tx_id = f"extrato_tx_{tx_counter}"
                        tx_counter += 1

                        t["transaction_id"] = tx_id
                        t["tags"] = classify_transaction(t.get("description", ""))
                        t["project_id"] = "PROJECT_ITAU_15220012"

                        out_f.write(json.dumps(t, ensure_ascii=False) + "\n")
                        total += 1

                    except Exception as e:
                        errors += 1
                        print(f"  ⚠ Error processing transaction: {e}")
                        continue

            except Exception as e:
                print(f"  ✗ Error processing {pdf_file}: {e}")
                continue

    print(f"\n✅ Extracted {total} transactions ({errors} errors)")
    print(f"   Output: {args.output}")
    if total == 0:
        print("   ⚠ Note: PDF parsing not yet implemented. Output is empty stub.")
        print("   Implement extract_transactions_from_pdf() with pdfplumber or similar.")


if __name__ == "__main__":
    main()
