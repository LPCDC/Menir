@echo off
REM Script de instalação rápida para Windows (CMD)
REM Execute como Administrador

echo === Menir - Instalacao Rapida para Neo4j Desktop ===
echo.

REM 1. Verificar Python
echo [1/4] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado. Instale Python 3.8+ de https://www.python.org/downloads/
    exit /b 1
)
echo [OK] Python encontrado
echo.

REM 2. Instalar neo4j driver
echo [2/4] Instalando neo4j driver...
pip install neo4j
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar neo4j driver
    exit /b 1
)
echo [OK] neo4j driver instalado
echo.

REM 3. Configurar variáveis de ambiente
echo [3/4] Configurando variaveis de ambiente...
set NEO4J_URI=neo4j://127.0.0.1:7687
set NEO4J_USER=neo4j
set NEO4J_PASSWORD=bvPp561reYBKtaNPwgPG4250tI9RFKcjNKkhoXG5dGc
set NEO4J_DB=neo4j
echo [OK] Variaveis configuradas
echo.

REM 4. Executar ingestão
echo [4/4] Executando ingestao completa...
echo   - Inicializando schema...
python livro_debora_cap1_ingest.py --init-schema
if %errorlevel% neq 0 (
    echo [ERRO] Falha na inicializacao do schema
    exit /b 1
)

echo   - Ingerindo dados do Capitulo 1...
python livro_debora_cap1_ingest.py --ensure-core --ingest-builtin
if %errorlevel% neq 0 (
    echo [ERRO] Falha na ingestao de dados
    exit /b 1
)

echo.
echo [OK] Ingestao concluida com sucesso!
echo.

REM 5. Executar auditoria
echo [BONUS] Executando auditoria do grafo...
python audit_livro_debora.py

echo.
echo === CONCLUIDO ===
echo Abra o Neo4j Browser e execute:
echo   MATCH (w:Work)-[:HAS_CHAPTER]-^>(c:Chapter) RETURN w, c
echo.
pause
