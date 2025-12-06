#!/usr/bin/env bash
# Script: clean_menir_grafo.sh
# Remove nós que não pertencem ao schema definido do Menir v2.
# Labels válidas: Work, Chapter, ChapterVersion, Scene, Event, Character, Place, Object, Chunk, EmotionState, SummaryNode

set -e

NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-menir123}"
NEO4J_DB="${NEO4J_DB:-neo4j}"

VALID_LABELS="Work|Chapter|ChapterVersion|Scene|Event|Character|Place|Object|Chunk|EmotionState|SummaryNode"

echo "=== Menir Graph Cleanup Script ==="
echo "URI: $NEO4J_URI"
echo "User: $NEO4J_USER"
echo "Database: $NEO4J_DB"
echo ""

# Função para executar queries via cypher-shell
run_query() {
    local query="$1"
    cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" -d "$NEO4J_DB" --format plain "$query"
}

# 1. Listar labels existentes
echo "[1/4] Listando todas as labels no grafo..."
run_query "CALL db.labels() YIELD label RETURN label ORDER BY label;"
echo ""

# 2. Contar nós fora do schema
echo "[2/4] Contando nós fora do schema..."
ORPHAN_COUNT=$(run_query "MATCH (n) WHERE NONE(lbl IN labels(n) WHERE lbl IN ['Work','Chapter','ChapterVersion','Scene','Event','Character','Place','Object','Chunk','EmotionState','SummaryNode']) RETURN count(n) AS orphanCount;" | tail -1)
echo "Nós fora do schema: $ORPHAN_COUNT"
echo ""

if [ "$ORPHAN_COUNT" = "0" ]; then
    echo "[INFO] Nenhum nó fora do schema encontrado. Grafo limpo!"
    exit 0
fi

# 3. Confirmar remoção
read -p "Deseja remover $ORPHAN_COUNT nós fora do schema? (s/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "[CANCELADO] Nenhum nó foi removido."
    exit 0
fi

# 4. Remover nós órfãos (fora do schema)
echo "[3/4] Removendo nós fora do schema..."
run_query "MATCH (n) WHERE NONE(lbl IN labels(n) WHERE lbl IN ['Work','Chapter','ChapterVersion','Scene','Event','Character','Place','Object','Chunk','EmotionState','SummaryNode']) WITH collect(n) AS toDelete UNWIND toDelete AS rem DETACH DELETE rem RETURN size(toDelete) AS deletedNodes;"
echo ""

# 5. Verificar limpeza
echo "[4/4] Verificando limpeza..."
REMAINING=$(run_query "MATCH (n) WHERE NONE(lbl IN labels(n) WHERE lbl IN ['Work','Chapter','ChapterVersion','Scene','Event','Character','Place','Object','Chunk','EmotionState','SummaryNode']) RETURN count(n) AS remaining;" | tail -1)
echo "Nós restantes fora do schema: $REMAINING"
echo ""

if [ "$REMAINING" = "0" ]; then
    echo "✓ Limpeza concluída com sucesso!"
else
    echo "⚠ Ainda existem $REMAINING nós fora do schema. Execute novamente se necessário."
fi

echo ""
echo "=== Resumo Final ==="
run_query "MATCH (n) RETURN labels(n)[0] AS nodeType, count(n) AS total ORDER BY total DESC;"

echo ""
echo "[DONE] Script de limpeza concluído."
