@echo off
REM ========================================================
REM Menir Utility — Reset senha Neo4j
REM Uso: rodar este script com a instância desligada
REM Caminho baseado na instância ativa do Desktop (.Neo4jDesktop2/Data)
REM ========================================================

SETLOCAL

REM 🔧 Ajuste o <ID_DA_INSTANCIA> conforme sua pasta real em .Neo4jDesktop2\Data\dbmss\
SET DBMS_ID=dbms-79dcc261-620f-4da2-9492-2f51e6661338
SET NEO4J_HOME=C:\Users\Pichau\.Neo4jDesktop2\Data\dbmss\%DBMS_ID%

ECHO === Resetando senha Neo4j na instância %DBMS_ID% ===

cd /d "%NEO4J_HOME%\bin"

CALL neo4j-admin.bat dbms set-initial-password nova_senha

ECHO ---
ECHO [OK] Senha resetada para 'nova_senha'
ECHO Reinicie a instância pelo Neo4j Desktop para aplicar.
ECHO ---

ENDLOCAL
pause
