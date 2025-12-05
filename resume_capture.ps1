# resume_capture.ps1
Set-Location "C:\Users\Pichau\Repos\MenirVital"

# tenta ler o último boot_now salvo (gerado antes pelo pause_session.ps1)
$lastBootJson = ""
if (Test-Path ".\last_boot_now.json") {
    $lastBootJson = Get-Content ".\last_boot_now.json" -Raw
}

Write-Host "=== Captura operacional ==="

$projRaw       = Read-Host "Nome curto do projeto (ex: tivoli)"
$summary       = Read-Host "Resumo do que aconteceu (1-2 linhas)"
$bloqueios     = Read-Host "Bloqueios principais (1-2 linhas)"
$prazoSketch   = Read-Host "Prazo sketch (YYYY-MM-DD)"
$prazoCAD      = Read-Host "Prazo CAD indicativo (YYYY-MM-DD)"
$participantes = Read-Host "Participantes chave separados por vírgula"

# slug curto e seguro p/ filename
$projSlug = ($projRaw.ToLower() -replace '[^a-z0-9_-]','-')
if ($projSlug.Length -gt 24) { $projSlug = $projSlug.Substring(0,24) }

# timestamp seguro pra filename (sem ":")
$tsFile   = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss'Z'")
$tsIso    = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

# garante pasta Core
$cypherDir = "projects\Core"
if (!(Test-Path $cypherDir)) {
    New-Item -ItemType Directory -Path $cypherDir | Out-Null
}

# arquivo .cypher com slug curto
$cypherFile = Join-Path $cypherDir ("session_${projSlug}_$tsFile.cypher")

$cypherContent = @"
MERGE (p:Projeto {id:'$projSlug'})
SET
  p.nome = '$projRaw',
  p.ultimo_update = datetime('$tsIso'),
  p.resumo = @'$summary',
  p.bloqueios = @'$bloqueios',
  p.prazo_sketch = date('$prazoSketch'),
  p.prazo_cad = date('$prazoCAD'),
  p.participantes = '$participantes';
"@

$cypherContent | Out-File -FilePath $cypherFile -Encoding UTF8

# BOOT_RESUME texto curto e sem ":"
$bootResume = @"
BOOT RESUME
branch_base: main
ultimo_boot_now_json: $lastBootJson
pendencias_abertas:
  - $bloqueios
  - sketch até $prazoSketch
  - CAD indicativo até $prazoCAD
  - acompanhamento projeto $projRaw
"@

$bootResumeFile = "BOOT_RESUME_$tsFile.txt"
$bootResume     | Out-File -FilePath $bootResumeFile -Encoding UTF8

Write-Host "=== Gerado ==="
Write-Host $cypherFile
Write-Host $bootResumeFile
Write-Host ""
Write-Host "Agora faça commit e push no GitHub Desktop com a mensagem:"
Write-Host "chore(log): captura operacional $projSlug $tsFile"
