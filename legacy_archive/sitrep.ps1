Write-Host "SEARCHING SYSTEM STATE..." -ForegroundColor Cyan

# 1. PHYSICAL ACCESS
Write-Host "`nFILES IN SRC/:" -ForegroundColor Yellow
if (Test-Path src) {
    Get-ChildItem src | Select-Object Name, LastWriteTime
}
else {
    Write-Host "ERROR: src/ folder NOT FOUND!" -ForegroundColor Red
}

# 2. LOGICAL ACCESS
Write-Host "`nBRAIN VERSION (Intel):" -ForegroundColor Yellow
if (Test-Path src/menir_intel.py) {
    Get-Content src/menir_intel.py -TotalCount 5
}
else {
    Write-Host "ERROR: src/menir_intel.py NOT FOUND!" -ForegroundColor Red
}

Write-Host "`nBRIDGE VERSION (Bridge):" -ForegroundColor Yellow
if (Test-Path src/menir_bridge.py) {
    Get-Content src/menir_bridge.py -TotalCount 5
}
else {
    Write-Host "ERROR: src/menir_bridge.py NOT FOUND!" -ForegroundColor Red
}

# 3 & 4. PYTHON CHECKS
python src/sitrep_check.py

Write-Host "`nEND OF REPORT."
