#!/usr/bin/env bash
set -e

# Change to workspace root
cd "$(dirname "$0")/.."

echo "🔐 Exportando credenciais da Aura"
export NEO4J_AURA_URI="neo4j+s://14dc1764.databases.neo4j.io:7687"
export NEO4J_AURA_USER="neo4j"
export NEO4J_AURA_PASSWORD="I7Dbf7wQEE3wsHQ1o3UB33I8vewoRrAWdtMcN0bVkY0"

echo "⚙️ Ativando virtualenv"
if [ -d ".venv" ]; then
  source .venv/bin/activate
else
  echo "❗ .venv não encontrado — criando e instalando dependências"
  python -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
fi

echo "🚚 Migrando dados do Neo4j local para Aura"
python migrate_incremental_to_aura.py

echo "🌱 Ingestão de documento de teste na Aura"
python - << 'PY'
from menir_core.graph_ingest import ingest_document
text = """
Capítulo de teste — introdução ao livro da Débora.
Este é um parágrafo fictício, inspirador, com tema de memória, culpa e reconstrução de vida. 
Serve para testar a ingestão e embeddings na instância remota (Aura).
"""
ingest_document(doc_id="teste_aura_doc1", title="Teste Aura Documento 1", full_text=text)
print("🧾 Documento de teste inserido com sucesso.")
PY

echo "✅ boot_to_aura completo — dados migrados + documento de teste criado."
