@echo off
setlocal ENABLEDELAYEDEXPANSION

REM === CONFIG ===
set REPO_PATH=C:\Users\Pichau\Repos\MenirVital
set BRANCH=release/menir-aio-v5.0-boot-local
set COMMIT_MSG=[auto-menir] bootstrap canonical contract

cd /d "%REPO_PATH%"
git checkout %BRANCH%
git pull origin %BRANCH%

REM vamos gerar via PowerShell todos os arquivos canônicos e o log de auditoria
set PS_TMP=%REPO_PATH%\_menir_bootstrap.ps1

> "%PS_TMP%" echo # gera arquivos canônicos do Menir e auditoria inicial
>>"%PS_TMP%" echo $tsUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

REM menir_state.json
>>"%PS_TMP%" echo $stateJson = @"
>>"%PS_TMP%" echo {
>>"%PS_TMP%" echo   "meta": {
>>"%PS_TMP%" echo     "boot_version": "v5.0",
>>"%PS_TMP%" echo     "branch_canonico": "release/menir-aio-v5.0-boot-local",
>>"%PS_TMP%" echo     "repo": "LPCDC/Menir",
>>"%PS_TMP%" echo     "timestamp_utc": "$tsUtc",
>>"%PS_TMP%" echo     "next_deadline": "2025-10-29T19:30:00-03:00"
>>"%PS_TMP%" echo   },
>>"%PS_TMP%" echo   "tasks": [
>>"%PS_TMP%" echo     "gerar Cypher incremental para novas Transacao Ita\u00FA",
>>"%PS_TMP%" echo     "gerar timeline Ita\u00FA limpa para assembleia sem sobrenomes completos"
>>"%PS_TMP%" echo   ],
>>"%PS_TMP%" echo   "schema": {
>>"%PS_TMP%" echo     "neo4j_labels_added": ["EventoBanco","Transacao"],
>>"%PS_TMP%" echo     "neo4j_rels_added": ["REFERE_A","ENVOLVENDO"],
>>"%PS_TMP%" echo     "evento_banco_anchor_id": "REG-2025-10-001",
>>"%PS_TMP%" echo     "conta_anchor_id": "15220012",
>>"%PS_TMP%" echo     "projeto_anchor_slug": "Itau"
>>"%PS_TMP%" echo   },
>>"%PS_TMP%" echo   "slowdown_guard": {
>>"%PS_TMP%" echo     "gpu_temp_c_max": 87,
>>"%PS_TMP%" echo     "latency_ms_max": 5000,
>>"%PS_TMP%" echo     "char_count_max": 90000
>>"%PS_TMP%" echo   },
>>"%PS_TMP%" echo   "push_policy": "manual_approval_required",
>>"%PS_TMP%" echo   "risk_notes": {
>>"%PS_TMP%" echo     "itau": "risco de rescis\u00E3o antecipada contratual ~53% antes de 2025-11-13 se n\u00E3o houver protocolo formal em 48h",
>>"%PS_TMP%" echo     "condominio": "assembleia Tivoli retrofit t\u00E9rreo e s\u00EDndico profissional. risco de retrabalho ~40%%",
>>"%PS_TMP%" echo     "gpu": "RTX 4070 Ti aproximando 87 C. risco de throttle ~25%%",
>>"%PS_TMP%" echo     "credencial": "exposi\u00E7\u00E3o de credencial \u00E9 risco alto. girar token se vazar"
>>"%PS_TMP%" echo   },
>>"%PS_TMP%" echo   "itau_context": "Linha do tempo banc\u00E1ria e efeito patrimonial ap\u00F3s assinatura 2025-09-29. Banco interno ainda n\u00E3o liberou cr\u00E9dito. Pedido formal de protocolo/registro, planilha CET, previs\u00E3o libera\u00E7\u00E3o p\u00F3s-registro.",
>>"%PS_TMP%" echo   "assembly_context": "Condom\u00EDnio Tivoli. Pauta retrofit t\u00E9rreo e s\u00EDndico profissional. Prazo interno Stage2.",
>>"%PS_TMP%" echo   "zk_log_digest": [
>>"%PS_TMP%" echo     {
>>"%PS_TMP%" echo       "hash": "SHA256:PLACEHOLDER",
>>"%PS_TMP%" echo       "action": "timeline_itau_generated",
>>"%PS_TMP%" echo       "ts_brt": "2025-10-27T20:40:00-03:00
