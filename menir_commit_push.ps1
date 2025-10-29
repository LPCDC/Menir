param([Parameter(Mandatory=$true)][string]$Message)

$repoPath = "C:\Users\Pichau\Repos\MenirVital"
$branch   = "release/menir-aio-v5.0-boot-local"

if (-not $env:GITHUB_PAT) {
    Write-Error "GITHUB_PAT not set"
    exit 1
}

$whitelist = @(
    "menir_state.json",
    "lgpd_policy.md",
    "output_contracts.md",
    "push_runbook.md",
    "logs/zk_audit.jsonl",
    "MENIR_COMMIT_POLICY.md",
    "commit_policy.json",
    "README_INSTALL.txt",
    "menir_commit_push.ps1",
    "menir_sync.cmd"
)

Set-Location $repoPath

git checkout $branch
git pull --ff-only origin $branch

$gitStatus = git status --porcelain
$changedFiles = $gitStatus | ForEach-Object { $_.Substring(3) } | Sort-Object -Unique

foreach ($cf in $changedFiles) {
    if ($whitelist -notcontains $cf) {
        Write-Error "blocked by whitelist: $cf"
        exit 1
    }
}

foreach ($f in $changedFiles) { git add $f }

$tsUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
$logEntry = @{
    ts_utc = $tsUtc
    action = "sync canonical state"
    result = "PENDING"
    details = $Message
    commit = "PENDING"
} | ConvertTo-Json -Compress
Add-Content "logs/zk_audit.jsonl" $logEntry
git add "logs/zk_audit.jsonl"

$finalMsg = "sync: $Message ts=$tsUtc"
git commit -m $finalMsg
if ($LASTEXITCODE -ne 0) { Write-Host "Nada a commitar."; exit 0 }

$remoteUrl = "https://LPCDC:$($env:GITHUB_PAT)@github.com/LPCDC/Menir.git"
git push $remoteUrl $branch
if ($LASTEXITCODE -ne 0) { Write-Error "push failed"; exit 1 }

$headHash = (git rev-parse HEAD).Trim()
$confirm = @{
    ts_utc = $tsUtc
    action = "sync canonical state"
    result = "OK"
    details = $Message
    commit = $headHash
} | ConvertTo-Json -Compress
Add-Content "logs/zk_audit.jsonl" $confirm
git add "logs/zk_audit.jsonl"
git commit -m "audit: zk confirm $headHash ts=$tsUtc"
git push $remoteUrl $branch

Write-Host "OK. HEAD=$headHash"
