@echo off
setlocal

REM Caminho local do repo oficial
cd /d C:\Users\Pichau\Repos\MenirVital

REM Garantir branch canônico
git checkout release/menir-aio-v5.0-boot-local

REM Trazer estado remoto mais recente só por segurança
git pull origin release/menir-aio-v5.0-boot-local

REM Criar/atualizar os 6 arquivos canônicos localmente
REM ATENCAO: copie o conteúdo a seguir manualmente ANTES de rodar o .bat:
REM - menir_state.json  (linhas 1..25 que você mostrou)
REM - lgpd_policy.md    (linhas 1..5)
REM - output_contracts.md (linhas 1..18)
REM - push_runbook.md   (linhas 1..11)
REM - logs\zk_audit.jsonl (linha 1)
REM - AGENTS.md         (bloco gerado acima)

REM Força inclusão do log porque logs/ está ignorado
git add menir_state.json lgpd_policy.md output_contracts.md push_runbook.md AGENTS.md
git add -f logs/zk_audit.jsonl

REM Commita com referência ao commit do container
git commit -m "[auto-menir] sync container commit 387676b into canonical branch"

REM Publica no GitHub
git push origin release/menir-aio-v5.0-boot-local

echo.
echo Se nao deu erro aqui, GitHub agora tem:
echo - menir_state.json
echo - lgpd_policy.md
echo - output_contracts.md
echo - push_runbook.md
echo - AGENTS.md
echo - logs/zk_audit.jsonl (audit trail)
echo.
pause
endlocal
