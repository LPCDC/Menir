# menir_boot_full.ps1

$scriptPath = $PSScriptRoot
Set-Location $scriptPath

Write-Host "==== MENIR BOOT FULL ====" -ForegroundColor Cyan

# 1. Health check
Write-Host "-- Healthcheck Neo4j --" -ForegroundColor Yellow
python scripts/menir_healthcheck_cli.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Healthcheck falhou. Abortando." -ForegroundColor Red
    exit 1
}

# 2. Ingestão
Write-Host "-- Ingestão de dados --" -ForegroundColor Yellow
python ingest/run_ingest_all.py

# 3. Dump / backup do grafo (se tiver script real; placeholder abaixo)
# Substitua pelo seu script real: dump_graph.ps1 ou comando equivalente
# Write-Host "-- Dump do grafo --"
# .\scripts\dump_graph.ps1

# 4. Limpeza de logs antigos
Write-Host "-- Limpeza de logs --" -ForegroundColor Yellow
python scripts/clean_logs.py

# 5. Checagem de segredos antes do push
Write-Host "-- Verificação de segredos (Gitleaks + TruffleHog) --" -ForegroundColor Yellow
# Verifica se make existe antes de tentar rodar
if (Get-Command "make" -ErrorAction SilentlyContinue) {
    make check-secrets
}
else {
    Write-Host "Aviso: 'make' não encontrado. Pulando check-secrets via Makefile." -ForegroundColor Magenta
    Write-Host "Dica: Instale make via 'choco install make' ou rode as ferramentas manualmente."
}

Write-Host "==== MENIR BOOT completo. Tudo pronto. ====" -ForegroundColor Green
