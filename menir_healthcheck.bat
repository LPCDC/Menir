@echo off
setlocal enabledelayedexpansion
set REPO=C:\Users\Pichau\Repos\Menir
set BRANCH=release/menir-aio-v5.0-boot-local

cd /d %REPO%
git fetch origin
git checkout %BRANCH%
git pull --ff-only

for /f "usebackq tokens=1-2 delims==" %%i in (`wmic path win32_timezone get bias ^| findstr /r "[0-9]"`) do set BIAS=%%i
REM timestamp simples
for /f %%i in ('powershell -NoP -C "(Get-Date).ToString(\"yyyy-MM-ddTHH:mm:ss-03:00\")"') do set TS_BRT=%%i
for /f %%i in ('powershell -NoP -C "(Get-Date).ToUniversalTime().ToString(\"yyyy-MM-ddTHH:mm:ssZ\")"') do set TS_UTC=%%i

REM Atualiza/Cria menir_state.json
powershell -NoP -C ^
  "$f='%REPO%\menir_state.json';" ^
  "if(Test-Path $f){$j=Get-Content $f -Raw|ConvertFrom-Json;$j.timestamp_brt='%TS_BRT%';$j|ConvertTo-Json -Depth 10|Out-File -Encoding UTF8 $f} else {@{timestamp_brt='%TS_BRT%';healthcheck='ops'}|ConvertTo-Json|Out-File -Encoding UTF8 $f}"

REM Audita
if not exist logs mkdir logs
if not exist logs\zk_audit.jsonl type nul > logs\zk_audit.jsonl
echo {"ts_utc":"%TS_UTC%","action":"ops.healthcheck","result":"PENDING"}>>logs\zk_audit.jsonl

git add menir_state.json logs\zk_audit.jsonl
git commit -m "healthcheck: ops test %DATE% %TIME%"
git push origin %BRANCH%

for /f %%i in ('git rev-parse HEAD') do set COMMIT=%%i
powershell -NoP -C ^
  "(Get-Content 'logs\zk_audit.jsonl' -Raw) -replace '\"PENDING\"', '\"OK\",\"commit\":\"%COMMIT%\"' | Out-File -Encoding UTF8 'logs\zk_audit.jsonl'"

git add logs\zk_audit.jsonl
git commit -m "audit: record commit %COMMIT%"
git push origin %BRANCH%

echo STATUS: OK | commit=%COMMIT%
endlocal
