#!/usr/bin/env bash
set -e

echo "==============================="
echo "  MENIR BOOTNOW – CODESPACE   "
echo "==============================="

# 1. .env (Menir + Neo4j)
if [ ! -f .env ]; then
  echo "⚙️  Criando .env padrão..."
  cat > .env << 'EOF'
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=menir123
MENIR_PROJECT_ID=livro_debora_cap1
EOF
else
  echo "ℹ️  .env já existe, mantendo."
fi

# 2. venv + dependências
if [ ! -d ".venv" ]; then
  echo "🐍 Criando venv (.venv)..."
  python -m venv .venv
fi

echo "🐍 Ativando venv..."
# shellcheck disable=SC1091
source .venv/bin/activate

if [ -f requirements.txt ]; then
  echo "📦 Instalando/atualizando dependências..."
  pip install --upgrade pip
  pip install -r requirements.txt
else
  echo "⚠️  requirements.txt não encontrado – pulando install."
fi

# 3. Neo4j via docker compose (reset seguro)
echo "🐳 Resetando Neo4j (docker compose down -v)..."
docker compose down -v || true

echo "🐳 Subindo Neo4j (docker compose up -d)..."
docker compose up -d

# 4. Esperar HTTP e Bolt ficarem online
echo "⏳ Aguardando Neo4j (HTTP 7474)..."
until curl -fsS http://localhost:7474 >/dev/null 2>&1; do
  echo -n "."
  sleep 2
done
echo ""
echo "✅ HTTP OK (7474)"

echo "⏳ Aguardando Bolt (7687)..."
python - << 'PYCODE'
import os, time
from neo4j import GraphDatabase, exceptions

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "menir123")

for i in range(10):
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        print("✅ Bolt OK (7687)")
        driver.close()
        break
    except exceptions.ServiceUnavailable as e:
        print(f"… aguardando Bolt (tentativa {i+1}/10): {e}")
        time.sleep(3)
else:
    raise SystemExit("❌ Bolt não respondeu após 10 tentativas.")
PYCODE

# 5. Seed de exemplo (sample_seed.py)
if [ -f "menir/seeds/sample_seed.py" ]; then
  echo "🌱 Rodando seed de exemplo (sample_seed.py)..."
  python menir/seeds/sample_seed.py
else
  echo "⚠️  menir/seeds/sample_seed.py não encontrado – pulando seed."
fi

# 6. Smoke tests Menir (conexão + vetores + embed/store)
echo "🧪 Rodando smoke tests Menir..."
python menir_core/test_neo4j_connection.py
python menir_core/test_vector_pipeline.py
python menir_core/embed_and_store.py

# 7. Demo de busca vetorial de quotes (end-to-end)
if [ -f "scripts/quote_vector_search.py" ]; then
  echo "🔍 Demo: busca vetorial de quotes..."
  python scripts/quote_vector_search.py \
    "memória, culpa do passado e reconstrução de vida" \
    --top-k 5
else
  echo "⚠️  scripts/quote_vector_search.py não encontrado – pulando demo."
fi

echo "🎉 BOOTNOW CODESPACE CONCLUÍDO."
echo "Menir + Neo4j + vetores prontos para uso."

