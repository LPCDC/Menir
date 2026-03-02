#!/usr/bin/env python3
"""
Limpeza de arquivos de log antigos (mais de 30 dias).
"""

import os
import sys
import time

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
# Corrigir path se script rodar de outro lugar, mas assumindo scripts/clean_logs.py
# O dirname(__file__) é .../scripts, então .. é root, + logs.

if not os.path.isdir(LOG_DIR):
    print(f"Aviso: diretório de logs não encontrado ({LOG_DIR}). Nada a fazer.")
    sys.exit(0)

now = time.time()
threshold = 30 * 86400  # 30 dias in seconds

removed = 0
try:
    for fname in os.listdir(LOG_DIR):
        path = os.path.join(LOG_DIR, fname)
        if os.path.isfile(path):
            age = now - os.path.getmtime(path)
            if age > threshold:
                os.remove(path)
                removed += 1
    print(f"Limpeza de logs: {removed} arquivos removidos.")
except Exception as e:
    print(f"Erro ao limpar logs: {e}")
    sys.exit(1)
