# Script de instalação rápida para Windows
# Execute no PowerShell como Administrador

Write-Host "=== Menir - Instalação Rápida para Neo4j Desktop ===" -ForegroundColor Green

# 1. Verificar Python
Write-Host "`n[1/4] Verificando Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python não encontrado. Instale Python 3.8+ de https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# 2. Instalar neo4j driver
Write-Host "`n[2/4] Instalando neo4j driver..." -ForegroundColor Cyan
pip install neo4j
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ neo4j driver instalado" -ForegroundColor Green
} else {
    Write-Host "✗ Falha ao instalar neo4j driver" -ForegroundColor Red
    exit 1
}

# 3. Configurar variáveis de ambiente
Write-Host "`n[3/4] Configurando variáveis de ambiente..." -ForegroundColor Cyan
$env:NEO4J_URI="neo4j://127.0.0.1:7687"
$env:NEO4J_USER="neo4j"
$env:NEO4J_PASSWORD="bvPp561reYBKtaNPwgPG4250tI9RFKcjNKkhoXG5dGc"
$env:NEO4J_DB="neo4j"
Write-Host "✓ Variáveis configuradas para esta sessão" -ForegroundColor Green

# 4. Executar ingestão
Write-Host "`n[4/4] Executando ingestão completa..." -ForegroundColor Cyan
Write-Host "  → Inicializando schema..." -ForegroundColor Yellow
python livro_debora_cap1_ingest.py --init-schema

if ($LASTEXITCODE -eq 0) {
    Write-Host "  → Ingerindo dados do Capítulo 1..." -ForegroundColor Yellow
    python livro_debora_cap1_ingest.py --ensure-core --ingest-builtin
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✓ Ingestão concluída com sucesso!" -ForegroundColor Green
        
        # 5. Executar auditoria
        Write-Host "`n[BONUS] Executando auditoria do grafo..." -ForegroundColor Cyan
        python audit_livro_debora.py
        
        Write-Host "`n=== CONCLUÍDO ===" -ForegroundColor Green
        Write-Host "Abra o Neo4j Browser e execute:" -ForegroundColor Cyan
        Write-Host "  MATCH (w:Work)-[:HAS_CHAPTER]->(c:Chapter) RETURN w, c" -ForegroundColor White
    } else {
        Write-Host "✗ Falha na ingestão de dados" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✗ Falha na inicialização do schema" -ForegroundColor Red
    exit 1
}
