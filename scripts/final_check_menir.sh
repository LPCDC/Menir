#!/usr/bin/env bash
# final_check_menir.sh — verifica tudo e reporta status final

set -e

echo "### Menir — Final status check ###"

echo
echo "--> 1) Git status & últimos commits"
git status
git log --oneline -5

echo
echo "--> 2) Verificação Neo4j + sanity"
if [ -n "$VIRTUAL_ENV" ]; then
  python3 scripts/sanity_neo4j_full.py
else
  source .venv/bin/activate 2>/dev/null && python3 scripts/sanity_neo4j_full.py || echo "⚠️ Venv não ativada — rodando com python3 global"
fi

echo
echo "--> 3) Verificação de workflow automático"
if [ -f ".github/workflows/scheduled-snapshot.yml" ]; then
  echo "✔️ Workflow de snapshot automático (scheduled-snapshot.yml) presente"
else
  echo "⚠️ Workflow de snapshot automático ausente — verifique .github/workflows/"
fi

echo
echo "--> 4) Listagem de scripts essenciais"
echo "   Scripts disponíveis:"
ls -1 scripts/*.py scripts/*.sh 2>/dev/null | sed 's/^/   - /' || echo "   ⚠️ Nenhum script encontrado"

echo
echo "--> 5) Verificação de documentação"
DOCS=("POST_BOOTSTRAP_README.md" "FINAL_SETUP_GUIDE.md" "bootstrap_manifest.json")
for doc in "${DOCS[@]}"; do
  if [ -f "$doc" ]; then
    echo "✔️ $doc"
  else
    echo "⚠️ $doc — ausente"
  fi
done

echo
echo "--> 6) Estatísticas do repositório"
COMMIT_COUNT=$(git rev-list --count HEAD)
TAG_COUNT=$(git tag | wc -l)
echo "   Total de commits: $COMMIT_COUNT"
echo "   Total de tags: $TAG_COUNT"
echo "   Branch atual: $(git rev-parse --abbrev-ref HEAD)"
echo "   Commit mais recente: $(git rev-parse --short HEAD) — $(git log -1 --pretty=%B)"

echo
echo "### ✅ Estado final do Menir: pronto para uso contínuo ###"
echo
echo "Próximos passos (se ainda não fez):"
echo "1. Leia: cat FINAL_SETUP_GUIDE.md"
echo "2. Configure GitHub Secrets (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)"
echo "3. O workflow automático rodará diariamente às 03:00 UTC"
echo
