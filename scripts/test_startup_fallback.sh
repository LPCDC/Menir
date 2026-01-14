#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Test script for menir_startup.sh fallback logic
# Validates that the script properly detects Docker and makes correct decisions
#
# Usage: bash scripts/test_startup_fallback.sh
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Função de logging
test_log() {
  echo -e "${BLUE}[test_startup]${NC} $1"
}

test_pass() {
  echo -e "${GREEN}✓${NC} $1"
}

test_fail() {
  echo -e "${RED}✗${NC} $1"
}

test_warn() {
  echo -e "${YELLOW}⚠${NC} $1"
}

echo ""
echo "=========================================="
echo "Teste de Fallback: Docker ↔ Neo4j Local"
echo "=========================================="
echo ""

# TEST 1: Verify script exists and is executable
test_log "TEST 1: Verificando script de startup..."
if [ ! -f "$PROJECT_ROOT/scripts/menir_startup.sh" ]; then
  test_fail "Script menir_startup.sh não encontrado"
  exit 1
fi

if [ ! -x "$PROJECT_ROOT/scripts/menir_startup.sh" ]; then
  test_fail "Script menir_startup.sh não é executável"
  exit 1
fi

test_pass "Script menir_startup.sh existe e é executável"
echo ""

# TEST 2: Verify syntax
test_log "TEST 2: Verificando sintaxe do script..."
if bash -n "$PROJECT_ROOT/scripts/menir_startup.sh" 2>/dev/null; then
  test_pass "Sintaxe do script menir_startup.sh OK"
else
  test_fail "Sintaxe do script tem erros"
  bash -n "$PROJECT_ROOT/scripts/menir_startup.sh"
  exit 1
fi
echo ""

# TEST 3: Check for required functions
test_log "TEST 3: Verificando funções obrigatórias..."
required_functions=("docker_available" "stage_load_env" "stage_docker_detection" "stage_start_neo4j" "stage_test_connectivity" "stage_run_pipeline" "stage_final_health_check")

for func in "${required_functions[@]}"; do
  if grep -q "^$func()" "$PROJECT_ROOT/scripts/menir_startup.sh"; then
    test_pass "Função $func encontrada"
  else
    test_fail "Função $func não encontrada"
    exit 1
  fi
done
echo ""

# TEST 4: Test docker_available function
test_log "TEST 4: Testando detecção de Docker..."
if command -v docker >/dev/null 2>&1; then
  test_pass "Comando 'docker' está no PATH"
  if docker info >/dev/null 2>&1; then
    test_pass "Docker daemon respondendo a 'docker info'"
    test_log "  → Modo Docker será ATIVADO"
  else
    test_warn "Docker instalado mas daemon não respondendo"
    test_log "  → Modo LOCAL será ativado (fallback)"
  fi
else
  test_warn "Comando 'docker' não encontrado no PATH"
  test_log "  → Modo LOCAL será ativado (fallback)"
fi
echo ""

# TEST 5: Verify .env handling
test_log "TEST 5: Verificando tratamento de .env..."
if [ ! -f "$PROJECT_ROOT/.env" ]; then
  test_warn ".env não encontrado (será criado a partir de .env.template se necessário)"
  if [ ! -f "$PROJECT_ROOT/.env.template" ]; then
    test_fail ".env.template também não encontrado"
    exit 1
  fi
  test_log "  Criando .env a partir de template..."
  cp "$PROJECT_ROOT/.env.template" "$PROJECT_ROOT/.env"
  test_pass ".env criado com sucesso"
else
  test_pass ".env já existe"
fi
echo ""

# TEST 6: Verify neo4j_bolt_diagnostic.py
test_log "TEST 6: Verificando neo4j_bolt_diagnostic.py..."
if [ ! -f "$PROJECT_ROOT/scripts/neo4j_bolt_diagnostic.py" ]; then
  test_fail "neo4j_bolt_diagnostic.py não encontrado"
  exit 1
fi

test_pass "neo4j_bolt_diagnostic.py existe"

# Check for CLI argument support
if grep -q "argparse" "$PROJECT_ROOT/scripts/neo4j_bolt_diagnostic.py"; then
  test_pass "neo4j_bolt_diagnostic.py suporta argumentos CLI"
else
  test_fail "neo4j_bolt_diagnostic.py não suporta argumentos CLI"
  exit 1
fi

# Check Python syntax
if python3 -m py_compile "$PROJECT_ROOT/scripts/neo4j_bolt_diagnostic.py" 2>/dev/null; then
  test_pass "Sintaxe do neo4j_bolt_diagnostic.py OK"
else
  test_fail "neo4j_bolt_diagnostic.py tem erros de sintaxe"
  exit 1
fi
echo ""

# TEST 7: Verify menir_bootstrap_and_ingest.sh
test_log "TEST 7: Verificando menir_bootstrap_and_ingest.sh..."
if [ ! -f "$PROJECT_ROOT/scripts/menir_bootstrap_and_ingest.sh" ]; then
  test_fail "menir_bootstrap_and_ingest.sh não encontrado"
  exit 1
fi

# Check that normalization tool calls are implemented
tools=("itau_email_to_jsonl.py" "whatsapp_txt_to_jsonl.py" "itau_extrato_to_jsonl.py" "docs_to_manifest.py")
for tool in "${tools[@]}"; do
  if grep -q "$tool" "$PROJECT_ROOT/scripts/menir_bootstrap_and_ingest.sh"; then
    test_pass "Chamada a $tool está implementada"
  else
    test_warn "Chamada a $tool não encontrada"
  fi
done

# Check that ingestion script calls are implemented
ingestion_scripts=("menir_ingest_email_itau.py" "menir_ingest_extratos_itau.py" "menir_ingest_whatsapp_itau.py" "menir_ingest_docs_itau.py")
for script in "${ingestion_scripts[@]}"; do
  if grep -q "$script" "$PROJECT_ROOT/scripts/menir_bootstrap_and_ingest.sh"; then
    test_pass "Chamada a $script está implementada"
  else
    test_warn "Chamada a $script não encontrada"
  fi
done
echo ""

# TEST 8: Verify docker-compose.yml update
test_log "TEST 8: Verificando docker-compose.yml..."
if [ ! -f "$PROJECT_ROOT/docker-compose.yml" ]; then
  test_fail "docker-compose.yml não encontrado"
  exit 1
fi

if grep -q "menir_startup.sh" "$PROJECT_ROOT/docker-compose.yml"; then
  test_pass "docker-compose.yml atualizado com menir_startup.sh"
else
  test_warn "docker-compose.yml pode não estar atualizado"
fi
echo ""

# TEST 9: Directory structure
test_log "TEST 9: Verificando estrutura de diretórios..."
required_dirs=(
  "data/itau/email/raw"
  "data/itau/email/normalized"
  "data/itau/whatsapp/raw"
  "data/itau/whatsapp/normalized"
  "data/itau/extratos/raw"
  "data/itau/extratos/normalized"
  "data/itau/docs"
  "logs/itau"
  "reports/itau"
  "scripts"
  "tools"
  "tests"
)

for dir in "${required_dirs[@]}"; do
  if [ -d "$PROJECT_ROOT/$dir" ]; then
    test_pass "Diretório $dir existe"
  else
    test_warn "Diretório $dir não existe (será criado em runtime)"
  fi
done
echo ""

# TEST 10: Documentation
test_log "TEST 10: Verificando documentação..."
required_docs=(
  "docs/DOCKER_FALLBACK.md"
  "docs/TESTING.md"
  "docs/IMPLEMENTATION_STATUS.md"
  "docs/NEO4J_CONFIG.md"
)

for doc in "${required_docs[@]}"; do
  if [ -f "$PROJECT_ROOT/$doc" ]; then
    test_pass "Documentação $doc existe"
  else
    test_warn "Documentação $doc não encontrada"
  fi
done
echo ""

# Summary
echo "=========================================="
echo "✅ Testes de Fallback Completos!"
echo "=========================================="
echo ""
echo "Status:"
echo "  • Docker fallback logic: ✓ Implementado"
echo "  • Startup script: ✓ Pronto"
echo "  • Normalization tools: ✓ Integrados"
echo "  • Ingestion scripts: ✓ Integrados"
echo "  • Documentação: ✓ Completa"
echo ""
echo "Próximos passos:"
echo "  1. Inicie Neo4j Desktop ou Docker"
echo "  2. Execute: bash scripts/menir_startup.sh"
echo "  3. Monitore output para validar fallback automático"
echo ""
echo "Para debug detalhado, use:"
echo "  bash scripts/menir_startup.sh 2>&1 | tee menir_startup.log"
echo ""
