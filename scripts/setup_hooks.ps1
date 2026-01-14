# setup_hooks.ps1
# Instala os hooks do git localmente

$gitDir = ".git"
$hooksDir = "$gitDir\hooks"
$sourceDir = "scripts\hooks"

if (-not (Test-Path $gitDir)) {
    Write-Host "Erro: Diretório .git não encontrado. Execute na raiz do repo." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $hooksDir)) {
    New-Item -ItemType Directory -Force -Path $hooksDir | Out-Null
}

$preCommitSource = "$sourceDir\pre-commit"
$preCommitDest = "$hooksDir\pre-commit"

if (Test-Path $preCommitSource) {
    Copy-Item -Path $preCommitSource -Destination $preCommitDest -Force
    Write-Host "Hook pre-commit instalado com sucesso em $preCommitDest" -ForegroundColor Green
}
else {
    Write-Host "Aviso: Hook fonte não encontrado em $preCommitSource" -ForegroundColor Yellow
}
