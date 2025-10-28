# ===== CONFIG =====
$RepoPath = "C:\Users\Pichau\Repos\MenirVital"            # pasta do repo LPCDC/Menir clonado
$Branch   = "release/menir-aio-v5.0-boot-local"
$User     = "LPCDC"                                  # seu usuário GitHub
$Repo     = "Menir"
$GHToken  = $env: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                       # defina antes:  setx GITHUB_TOKEN "ghp_xxx"
$Neo4jBin = "C:\Program Files\Neo4j\bin"             # ajuste se preciso
$Neo4jUser= "neo4j"
$Neo4jPass= "bvPp561reYBKtaNPwgPG4250tI9RFKcjNKkhoXG5dGc"                            # preencha
$DbName   = "neo4j"                                  # ajuste se usa outro DB
# ===================

# Fail fast
$ErrorActionPreference = "Stop"

# 0) Preflight Git
Set-Location $RepoPath
git fetch origin
git checkout $Branch
git pull --ff-only

# 1) Touch: menir_state.json (timestamp) e logs/zk_audit.jsonl
$ts_brt = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss-03:00")
$stateFile = Join-Path $RepoPath "menir_state.json"
$logFile   = Join-Path $RepoPath "logs\zk_audit.jsonl"

# Atualiza somente timestamp_brt se existir a chave; senão, cria um mínimo
if (Test-Path $stateFile) {
  $json = Get-Content $stateFile -Raw | ConvertFrom-Json
  $json.timestamp_brt = $ts_brt
  ($json | ConvertTo-Json -Depth 10) | Out-File -Encoding UTF8 $stateFile
} else {
  @{ timestamp_brt=$ts_brt; healthcheck="ops"; branch=$Branch } | ConvertTo-Json | Out-File -Encoding UTF8 $stateFile
}

# Linha de auditoria
$ts_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
if (-not (Test-Path $logFile)) { New-Item -Force -ItemType File $logFile | Out-Null }
'{"ts_utc":"'+$ts_utc+'","action":"ops.healthcheck","result":"PENDING"}' | Out-File -Append -Encoding UTF8 $logFile

# 2) Commit
git add menir_state.json logs/zk_audit.jsonl
git commit -m "healthcheck: ops test $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git push origin $Branch

# 3) Captura hash do último commit local
$commit = (git rev-parse HEAD).Trim()

# 4) Atualiza linha PENDING -> OK (com hash) e commita
(Get-Content $logFile -Raw) -replace '"PENDING"' , ('"OK","commit":"'+$commit+'"') | Out-File -Encoding UTF8 $logFile
git add logs/zk_audit.jsonl
git commit -m "audit: record commit $commit"
git push origin $Branch

# 5) Verificação via API GitHub (status/visibilidade do commit)
if ([string]::IsNullOrEmpty($GHToken)) { Write-Warning "GITHUB_TOKEN não definido. Pulei checagem API."; }
else {
  $headers = @{ Authorization = "Bearer $GHToken"; "X-GitHub-Api-Version"="2022-11-28" }
  $urlCommit = "https://api.github.com/repos/$User/$Repo/commits/$commit"
  $resp = Invoke-RestMethod -Headers $headers -Uri $urlCommit -Method GET
  Write-Host ("GitHub OK: commit visível = " + $resp.sha.Substring(0,7))
}

# 6) Neo4j: teste rápido (conexão, write/read)
$cypherShell = Join-Path $Neo4jBin "cypher-shell.bat"
$test1 = 'RETURN 1 AS ok;'
$test2 = 'CREATE (h:Healthcheck {ts:"'+$ts_utc+'", tag:"ops"}) RETURN id(h) AS id;'
$test3 = 'MATCH (h:Healthcheck {tag:"ops"}) WHERE h.ts="'+$ts_utc+'" DETACH DELETE h; RETURN "deleted" AS d;'

& $cypherShell -u $Neo4jUser -p $Neo4jPass -d $DbName $test1 | Out-Host
& $cypherShell -u $Neo4jUser -p $Neo4jPass -d $DbName $test2 | Out-Host
& $cypherShell -u $Neo4jUser -p $Neo4jPass -d $DbName $test3 | Out-Host

Write-Host ("STATUS: OK | commit="+$commit)
