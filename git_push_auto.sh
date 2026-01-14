#!/usr/bin/env bash

# Snippet: push automático no branch atual, sem hard-code de "main"

# detecta o nome do branch atual
BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ -z "$BRANCH" ]; then
  echo "Erro: não consegui detectar o branch atual."
  exit 1
fi

echo "Branch atual: $BRANCH"

# adiciona todas mudanças e comita se houver staged changes
git add -A
if git diff --cached --quiet; then
  echo "Nada novo para commitar."
else
  git commit -m "chore: atualiza scripts / audit – branch $BRANCH"
  echo "Commit feito no branch $BRANCH."
fi

# tenta push
git push origin "$BRANCH"
RET=$?

if [ $RET -ne 0 ]; then
  echo "Push falhou. Revise se o remoto e o nome do branch estão corretos."
  exit $RET
fi

echo "Push para origin/$BRANCH realizado com sucesso."
