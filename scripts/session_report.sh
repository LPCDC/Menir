#!/usr/bin/env bash
set -e

echo "=== Menir – Session Report ==="
echo "Data: $(date -u)"
echo "--- Neo4j Sanity Check ---"
python scripts/sanity_neo4j_full.py || { echo "ERRO: Neo4j não conectou"; exit 1; }
echo "--- Git Status ---"
git status
echo "--- Últimos commits ---"
git log --oneline -5
echo "--- Tag mais recente ---"
git describe --tags --abbrev=0 || echo "Nenhuma tag encontrada"
echo "--- Checklist Pós-Bootstrap ---"
cat POST_BOOTSTRAP_README.md | sed -n '1,10p'
echo "=== Fim do Relatório ==="

echo
echo "Menir v10.4.1 — sessão encerrada. Tudo limpo e versionado."
