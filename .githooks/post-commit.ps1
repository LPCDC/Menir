# Powershell wrapper para post-commit
$scriptPath = Join-Path (git rev-parse --show-toplevel) ".githooks/post-commit.sh"
bash "$scriptPath"
