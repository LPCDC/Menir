#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."  # assume structure scripts/ finalize → volta à raiz do repo

echo "=== Menir 10.2 — Início do processo de finalização ==="

echo "1) Atualizando repositório main"
git checkout main
git pull --ff-only

echo "2) Rodando testes de logging"
PYTHONPATH=. pytest -q test_menir10_log.py

echo "3) Preparando commit final se houver mudanças"
git add menir10/menir10_log.py scripts/menir10_log_cli.py menir_state.json projects/SaintCharles projects/SaintCharles/README_SAINT_CHARLES.md 2>/dev/null || true
if ! git diff-index --quiet HEAD --; then
  git commit -m "Menir 10.2: finalize logging canônico + Saint Charles + menir_state"
else
  echo "   → Nada para commitar."
fi

echo "4) Enviando para remoto"
git push origin main

echo "5) Criando tag 10.2"
git tag -a menir-10.2 -m "Menir 10.2 – logging canônico + Saint Charles + menir_state"
git push origin menir-10.2

echo "6) Smoke-test do CLI de log"
export MENIR_PROJECT_ID=SaintCharles_CM2025
PYTHONPATH=. python scripts/menir10_log_cli.py -c "Smoke test Menir 10.2 – Saint Charles" --intent-profile boot
PYTHONPATH=. python scripts/menir10_log_cli.py -p itau_15220012 -c "Smoke test Menir 10.2 – Itaú" --intent-profile note

echo "7) Últimas 3 linhas do log de interações"
tail -n 3 logs/menir10_interactions.jsonl

echo "=== Menir 10.2 FINALIZADO com sucesso ==="
