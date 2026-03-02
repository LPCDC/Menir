#!/usr/bin/env bash

# check_contrib.sh — script para validar contribuições básicas do Training U

# Saída colorida
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

errors=0

# 1. Verificar se checkpoint.md ou menir_meta_log.jsonl foi modificado
if git diff --name-only HEAD~1 HEAD | grep -qE "(checkpoint\.md|menir_meta_log\.jsonl)"; then
  echo -e "${GREEN}✔ checkpoint ou meta_log modificado${NC}"
else
  echo -e "${RED}✘ Atenção: checkpoint.md ou menir_meta_log.jsonl NÃO foi modificado.${NC}"
  errors=$((errors+1))
fi

# 2. Verificar prefixo de commit
# Obtém a última mensagem de commit
last_msg=$(git log -1 --pretty=%B)

if echo "$last_msg" | grep -qE "^(feat:|fix:|docs:|refactor:|trigger:|chore:)"; then
  echo -e "${GREEN}✔ Mensagem de commit com prefixo OK${NC}"
else
  echo -e "${RED}✘ Mensagem de commit deve iniciar com prefixo como feat:, fix:, docs:, refactor:, trigger:, chore:${NC}"
  errors=$((errors+1))
fi

# 3. Verificar se há novo gatilho definido e seed correspondente (simplificação)
if git diff --name-only HEAD~1 HEAD | grep -q "seeds/gatilhos_seed.cypher"; then
  echo -e "${GREEN}✔ seeds/gatilhos_seed.cypher foi modificado (possível novo gatilho)${NC}"
else
  echo -e "${GREEN}ℹ nenhum novo gatilho detectado nesta alteração${NC}"
fi

# Resultado final
if [ "$errors" -gt 0 ]; then
  echo -e "${RED}✘ Foram detectados ${errors} erro(s). Corrija antes de PR ou merge.${NC}"
  exit 1
else
  echo -e "${GREEN}✔ Tudo parece OK para contribuição!${NC}"
  exit 0
fi
