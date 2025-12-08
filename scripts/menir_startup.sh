#!/usr/bin/env bash
# -*- coding: utf-8 -*-
set -euo pipefail

#############################################################################
# Menir Startup Script — Fallback automático Docker ↔ Neo4j Desktop
#############################################################################
#
# Objetivo:
#   1. Carrega variáveis de .env
#   2. Detecta se Docker está disponível
#   3. Se sim: inicia Neo4j em container via docker-compose
#   4. Se não: assume instância local (Neo4j Desktop) e prossegue
#   5. Testa conectividade com Neo4j
#   6. Invoca pipeline de bootstrap + ingestão
#
# Uso:
#   bash scripts/menir_startup.sh
#   ou, em docker-compose:
#   command: bash -c "sleep 5 && ./scripts/menir_startup.sh"
#
# Variáveis de Ambiente (de .env):
#   NEO4J_URI     - Bolt URI (ex: bolt://localhost:7687)
#   NEO4J_USER    - Username (padrão: neo4j)
#   NEO4J_PWD     - Password
#   NEO4J_DB      - Database name (padrão: neo4j)
#   MENIR_PROJECT_ID - Project ID (padrão: ITAU_15220012)
#
#############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log_info() {
  echo -e "${BLUE}[menir_startup]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[menir_startup]${NC} ✓ $1"
}

log_warn() {
  echo -e "${YELLOW}[menir_startup]${NC} ⚠ $1"
}

log_error() {
  echo -e "${RED}[menir_startup]${NC} ✗ $1"
}

# ==================== STAGE 1: Load Environment ====================
stage_load_env() {
  log_info "STAGE 1: Carregando variáveis de ambiente..."

  if [ ! -f "$PROJECT_ROOT/.env" ]; then
    log_error "Arquivo .env não encontrado em $PROJECT_ROOT/"
    log_warn "Usando .env.template como referência — copie e configure:"
    log_warn "  cp $PROJECT_ROOT/.env.template $PROJECT_ROOT/.env"
    exit 1
  fi

  # Sourcing .env
  cd "$PROJECT_ROOT"
  set -a
  source .env
  set +a

  # Valores padrão se não estiverem em .env
  export NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
  export NEO4J_USER="${NEO4J_USER:-neo4j}"
  export NEO4J_PWD="${NEO4J_PWD:-menir123}"
  export NEO4J_DB="${NEO4J_DB:-neo4j}"
  export MENIR_PROJECT_ID="${MENIR_PROJECT_ID:-ITAU_15220012}"

  log_success "Variáveis carregadas:"
  log_info "  NEO4J_URI: $NEO4J_URI"
  log_info "  NEO4J_USER: $NEO4J_USER"
  log_info "  NEO4J_DB: $NEO4J_DB"
  log_info "  MENIR_PROJECT_ID: $MENIR_PROJECT_ID"
}

# ==================== STAGE 2: Docker Detection ====================
docker_available() {
  # Checa se comando 'docker' está no PATH
  if ! command -v docker >/dev/null 2>&1; then
    return 1
  fi

  # Checa se Docker daemon responde
  docker info >/dev/null 2>&1
  return $?
}

stage_docker_detection() {
  log_info "STAGE 2: Detectando disponibilidade de Docker..."

  if docker_available; then
    log_success "Docker disponível — modo CONTAINER ativado"
    export DOCKER_MODE=true
    return 0
  else
    log_warn "Docker não disponível — modo LOCAL ativado"
    log_warn "Assumindo instância Neo4j Desktop em $NEO4J_URI"
    export DOCKER_MODE=false
    return 0
  fi
}

# ==================== STAGE 3: Start Neo4j (Docker or Local) ====================
stage_start_neo4j() {
  log_info "STAGE 3: Iniciando Neo4j..."

  if [ "$DOCKER_MODE" = true ]; then
    log_info "Iniciando Neo4j container via docker-compose..."
    cd "$PROJECT_ROOT"

    # Verifica se docker-compose.yml existe
    if [ ! -f docker-compose.yml ]; then
      log_error "docker-compose.yml não encontrado"
      exit 1
    fi

    # Tenta parar container existente (gracefully)
    log_info "Verificando container existente..."
    docker-compose down || true

    # Inicia Neo4j
    docker-compose up -d neo4j

    log_info "Aguardando Neo4j subir (10 segundos)..."
    sleep 10

    # Verifica se container está rodando
    if ! docker-compose ps neo4j | grep -q "Up"; then
      log_error "Neo4j container não iniciou corretamente"
      docker-compose logs neo4j | tail -20
      exit 1
    fi

    log_success "Neo4j container iniciado com sucesso"
  else
    log_info "Modo LOCAL — pulando inicialização de container"
    log_info "Verifique se Neo4j Desktop está rodando em $NEO4J_URI"
  fi
}

# ==================== STAGE 4: Test Connectivity ====================
stage_test_connectivity() {
  log_info "STAGE 4: Testando conectividade com Neo4j..."

  cd "$PROJECT_ROOT"

  # Executa diagnóstico Bolt
  if python3 scripts/neo4j_bolt_diagnostic.py \
    --uri "$NEO4J_URI" \
    --user "$NEO4J_USER" \
    --password "$NEO4J_PWD" \
    --db "$NEO4J_DB"; then
    log_success "Conectividade Neo4j OK"
    return 0
  else
    log_error "Falha na conexão com Neo4j"
    log_warn "Verifique:"
    log_warn "  - Neo4j está rodando?"
    log_warn "  - Credenciais corretas em .env?"
    log_warn "  - Firewall/rede permitindo acesso a $NEO4J_URI?"

    if [ "$DOCKER_MODE" = true ]; then
      log_warn "Logs do container:"
      docker-compose logs neo4j | tail -30
    fi

    exit 1
  fi
}

# ==================== STAGE 5: Run Bootstrap & Ingest ====================
stage_run_pipeline() {
  log_info "STAGE 5: Executando pipeline de bootstrap + ingestão..."

  cd "$PROJECT_ROOT"

  if [ ! -f scripts/menir_bootstrap_and_ingest.sh ]; then
    log_error "scripts/menir_bootstrap_and_ingest.sh não encontrado"
    exit 1
  fi

  bash scripts/menir_bootstrap_and_ingest.sh

  if [ $? -eq 0 ]; then
    log_success "Pipeline concluído com sucesso"
    return 0
  else
    log_error "Pipeline falhou"
    exit 1
  fi
}

# ==================== STAGE 6: Final Health Check ====================
stage_final_health_check() {
  log_info "STAGE 6: Executando verificação final de saúde..."

  cd "$PROJECT_ROOT"

  if [ ! -f menir_healthcheck_full.py ]; then
    log_warn "menir_healthcheck_full.py não encontrado — pulando health check"
    return 0
  fi

  python3 menir_healthcheck_full.py

  log_success "Health check concluído"
}

# ==================== Main Execution ====================
main() {
  local start_time=$(date +%s)

  echo ""
  log_info "================================"
  log_info "Menir Startup — Fallback Docker/Local"
  log_info "================================"
  echo ""

  # Executa stages sequencialmente
  stage_load_env
  echo ""

  stage_docker_detection
  echo ""

  stage_start_neo4j
  echo ""

  stage_test_connectivity
  echo ""

  stage_run_pipeline
  echo ""

  stage_final_health_check
  echo ""

  local end_time=$(date +%s)
  local duration=$((end_time - start_time))

  echo ""
  log_success "================================"
  log_success "Menir Startup Completo!"
  log_success "Tempo total: ${duration}s"
  log_success "================================"
  echo ""
}

# Executa main, capturando erros
if main; then
  exit 0
else
  log_error "Startup falhou"
  exit 1
fi
