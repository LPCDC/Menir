# .githooks/post-commit.ps1
# Hook Git pós-commit – roda no Windows PowerShell

$ts = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$hash = (git rev-parse --short HEAD)
$author = (git log -1 --pretty=format:'%an')
$msg = (git log -1 --pretty=format:'%s')

$checkpointDir = "checkpoints"
$logFile = "$checkpointDir\last_hook.log"
$checkpointFile = "$checkpointDir\${ts}_${hash}.diff"

if (!(Test-Path $checkpointDir)) { New-Item -ItemType Directory -Path $checkpointDir | Out-Null }

Add-Content $logFile "[HOOK] Commit $hash by $author → '$msg' em $ts"

# Se arquivos Cypher mudaram, salva diff
$changedFiles = git diff-tree --no-commit-id --name-only -r HEAD
if ($changedFiles -match "^cypher/") {
    git diff HEAD^ HEAD | Out-File -Encoding utf8 $checkpointFile
    Add-Content $logFile "[HOOK] Checkpoint salvo: $checkpointFile"

    # Rodar validação no Neo4j Aura
    & cypher-shell -a "neo4j+s://085c38f7.databases.neo4j.io" `
        -u "neo4j" `
        -p "bvPp561reYBKtaNPwgPG4250tI9RFKcjNKkhoXG5dGc" `
        -f "cypher/validate_claims_final.cypher" | Out-File -Append $logFile
}
else {
    Add-Content $logFile "[HOOK] Sem mudanças em cypher/, sem checkpoint"
}
