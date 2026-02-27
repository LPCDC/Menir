#!/usr/bin/env pwsh
# menir_audit.ps1 — Auditoria automática de pré-deploy / pré-commit para Menir

function Report {
    param($msg, $kind = "INFO")
    $time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$time] [$kind] $msg"
}

$errors = 0

Report "=== Início da auditoria Menir ==="

# 1. Verificar .env
$env_path = ".\.env"
if (-Not (Test-Path $env_path)) {
    Report ".env não encontrado — credenciais ausentes." "ERROR"
    $errors++
}
else {
    $content = Get-Content $env_path -ErrorAction SilentlyContinue
    if ($content -match "NEO4J_URI=.*" -and $content -match "NEO4J_USER=.*" -and $content -match "NEO4J_PWD=.*") {
        Report ".env presente e parece conter variáveis de Neo4j."
    }
    else {
        Report ".env existe porém faltam variáveis Neo4j ou formato incorreto." "ERROR"
        $errors++
    }
}

# 2. Verificar .env está em .gitignore
$gi = Get-Content ".gitignore" -ErrorAction SilentlyContinue
if ($gi -match "(^|`n)\.env($|/)") {
    Report ".env está listado no .gitignore — OK."
}
else {
    Report ".env não está no .gitignore — risco de vazamento de credenciais." "WARN"
}

# 3. Verificar estrutura mínima de diretórios
$required = @("scripts", "logs")
foreach ($d in $required) {
    if (Test-Path $d) {
        Report "Diretório '$d' existe."
    }
    else {
        Report "Diretório '$d' não encontrado — estrutura incompleta." "ERROR"
        $errors++
    }
}

# 4. Checar se Makefile existe e contém targets essenciais
if (Test-Path "Makefile") {
    $mf = Get-Content "Makefile"
    $needed = @("healthcheck", "clean-logs", "dump-graph", "check-secrets")
    foreach ($t in $needed) {
        # Regex ajustada para pegar target seguido de :
        if ($mf -match "$t\s*:") {
            Report "Makefile contém target '$t'."
        }
        else {
            Report "Makefile não parece conter target '$t' — verificar." "WARN"
        }
    }
}
else {
    Report "Makefile não encontrado." "WARN"
}

# 5. Verificar se ferramentas de scan (gitleaks e/ou trufflehog) estão instaladas (opcional)
$gl = Get-Command gitleaks -ErrorAction SilentlyContinue
if ($gl) {
    Report "Gitleaks disponível."
}
else {
    Report "Gitleaks não encontrado — scan de segredos não será automático." "WARN"
}
# TruffleHog pode estar instalado via pip
Try {
    python -c "import trufflehog3" | Out-Null
    Report "TruffleHog (via Python) parece instalado."
}
Catch {
    Report "TruffleHog não detectado via Python — scan histórico pode falhar." "WARN"
}

# 6. Verificação de histórico/git — segredos potencialmente expostos (light scan)
# Usa gitleaks se disponível, senão avisa
if ($gl) {
    Report "Executando gitleaks detect — histórico será verificado..."
    & gitleaks detect --source . --exit-code 1 --report-path audit_gitleaks_report.json
    if ($LASTEXITCODE -eq 0) {
        Report "Gitleaks: nenhum segredo detectado."
    }
    else {
        Report "Gitleaks detectou possíveis segredos — ver audit_gitleaks_report.json" "ERROR"
        $errors++
    }
}
else {
    Report "Skip scan de histórico — gitleaks ausente." "WARN"
}

# 7. Health-check (se credenciais estiverem presentes)
if ((Test-Path $env_path) -and ($content -match "NEO4J_URI=.*")) {
    Report "Rodando health-check do grafo Neo4j..."
    python scripts/menir_healthcheck_cli.py
    if ($LASTEXITCODE -eq 0) {
        Report "Health-check bem-sucedido."
    }
    else {
        Report "Health-check falhou — ver credenciais ou conexão Neo4j." "ERROR"
        $errors++
    }
}
else {
    Report "Pulando health-check (credenciais ausentes ou .env inválido)." "WARN"
}

# 8. Finalização
if ($errors -gt 0) {
    Report "Auditoria finalizada com $errors erro(s). Corrija antes de commit/push." "ERROR"
    exit 1
}
else {
    Report "Auditoria concluída sem erros — pronto para commit/push." "INFO"
    exit 0
}
