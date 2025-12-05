#!/usr/bin/env bash
set -e

echo "🚀  Iniciando setup Menir + Neo4j"

# 1. Gera/atualiza .env (caso não exista)
if [ ! -f .env ]; then
  cat > .env << 'EOF'
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=menir123
MENIR_PROJECT_ID=livro_debora_cap1
EOF
  echo "✅  .env criado"
else
  echo "ℹ️  .env já existe — mantendo"
fi

# 2. Levanta Neo4j via docker-compose
docker-compose up -d

echo "⏳  Aguardando container Neo4j ficar 'healthy'..."
# Espera até healthcheck marcar como healthy (ou erro)
until [ "$(docker inspect --format='{{.State.Health.Status}}' menir-graph)" = "healthy" ]; do
  echo -n "."
  sleep 2
done
echo "✅  Neo4j pronto (healthy)"

# 3. Rodar seed — ajuste conforme localização do seu script de seed
if [ -f menir/seeds/debora_bim_seed.py ]; then
  echo "🌱  Executando seed do grafo..."
  source .venv/bin/activate
  python menir/seeds/debora_bim_seed.py
  echo "✅  Seed concluída"
else
  echo "⚠️  Script de seed não encontrado (pulei esta etapa)"
fi

# 4. Rodar testes de fumaça / sanity check
echo "🧪  Executando testes básicos (conexão / embeddings / store / CLI)..."
source .venv/bin/activate
python menir_core/test_neo4j_connection.py
python menir_core/test_vector_pipeline.py
python menir_core/embed_and_store.py
python -c "print('✅  Smoke tests OK')"

echo "🎉  Setup Menir concluído."
