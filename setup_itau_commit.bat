@echo off
REM ==========================================================
REM Script BAT - Projeto Itaú (Menir)
REM Cria pasta + arquivos CSV de teste + commit + push automático
REM ==========================================================

SET BASE_DIR=%~dp0projects\Itau
SET COMMIT_MSG=proj:Itau add sample CSVs (transacoes, documentos, partes)

echo 📂 Criando pastas...
mkdir "%BASE_DIR%"

echo 📄 Criando CSVs de exemplo...
(
echo transacao_id,conta_id,data,valor,tipo,descricao,agencia,numero
echo tx001,123,2025-09-18,500.00,debito,"Pagamento teste",0001,98765
echo tx002,123,2025-09-19,1500.00,credito,"Depósito teste",0001,98765
) > "%BASE_DIR%\itau_transacoes.csv"

(
echo doc_id,conta_id,nome,data,tipo
echo doc001,123,Extrato_Setembro,2025-09-30,extrato
) > "%BASE_DIR%\itau_documentos.csv"

(
echo parte_id,conta_id,nome,tipo
echo p001,123,Luiz_Paulo,cliente
echo p002,123,Banco_Itau,banco
) > "%BASE_DIR%\itau_partes.csv"

echo ✅ Arquivos criados.

echo ==========================================================
echo 🔄 Fazendo commit e push...
cd %~dp0
git add projects\Itau\*.csv
git commit -m "%COMMIT_MSG%"
git push origin main

echo ==========================================================
echo ✅ Projeto Itaú pronto: CSVs criados, commitado e enviado.
pause
