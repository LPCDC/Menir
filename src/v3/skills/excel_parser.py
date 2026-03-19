import pandas as pd
import re
import os
import logging
from typing import Any, Dict, List

logger = logging.getLogger("BecoExcelParser")

class BecoExcelParser:
    """
    Parser especializado para as faturas em Excel da BECO (Nicole).
    """
    def __init__(self):
        pass

    def parse(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo nao encontrado: {file_path}")

        # Ler excel sem cabecalho
        df = pd.read_excel(file_path, header=None)
        
        # Mapeamento baseado na inspecao de BECO_01.2026
        # Pandas usa zero-indexed (Row 9 no Excel log = Index 9 no DF se lido puro)
        
        # 1. Dados do Cliente (D10, D11, D12)
        client_name = str(df.iloc[9, 3]).strip()
        client_addr1 = str(df.iloc[10, 3]).strip() if not pd.isna(df.iloc[10, 3]) else ""
        client_addr2 = str(df.iloc[11, 3]).strip() if not pd.isna(df.iloc[11, 3]) else ""
        client_address = f"{client_addr1} {client_addr2}".strip()

        # 2. Numero da Fatura e Data (B20, B21)
        raw_date = str(df.iloc[19, 1])
        raw_inv_num = str(df.iloc[20, 1])
        
        # date : 27.02.2026
        invoice_date = ""
        date_match = re.search(r"date\s*:\s*(\d{2}\.\d{2}\.\d{4})", raw_date, re.I)
        if date_match:
            invoice_date = date_match.group(1)
            
        # numero de facture: 6026/2026
        invoice_number = ""
        num_match = re.search(r"numéro de facture\s*:\s*(.*)", raw_inv_num, re.I)
        if num_match:
            invoice_number = num_match.group(1).strip()

        # 2b. Data de referencia do nome do arquivo (ex: 01.2026)
        referential_date = ""
        basename = os.path.basename(file_path)
        ref_match = re.search(r"(\d{2})\.(\d{4})", basename)
        if ref_match:
            # Se achamos 01.2026, criamos data 01.01.2026 para match
            referential_date = f"01.{ref_match.group(1)}.{ref_match.group(2)}"

        # 3. Tabela de Servicos (Inicia na Row 24 ou 26)
        services = []
        # Procurar o cabecalho "Description"
        start_row = 23
        for i in range(20, 26):
            if "Description" in str(df.iloc[i, 1]):
                start_row = i + 1
                break

        # Iterar ate encontrar "solde en notre faveur"
        total_amount = 0.0
        for i in range(start_row, len(df)):
            desc = str(df.iloc[i, 1]).strip()
            if "solde en notre faveur" in desc.lower():
                # Coluna 4 (E) tem o total
                try:
                    total_amount = float(df.iloc[i, 4])
                except:
                    total_amount = 0.0
                break
            
            # Se a linha for de servico (tem quantidade)
            qty = df.iloc[i, 2]
            if not pd.isna(qty) and str(qty).strip() != "":
                try:
                    services.append({
                        "description": desc,
                        "quantity": float(qty),
                        "unit_price": float(df.iloc[i, 3]),
                        "total_price": float(df.iloc[i, 4])
                    })
                except Exception as e:
                    logger.warning(f"Erro ao parsear linha {i} de servico: {e}")

        return {
            "client_name": client_name,
            "client_address": client_address,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "referential_date": referential_date,
            "services": services,
            "total_amount": total_amount,
            "currency": "CHF",
            "source_file": os.path.basename(file_path)
        }
