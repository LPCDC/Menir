@echo off
title Menir V5.2 - Bisturi Nuclear (Zero-Bloat)
color 0C

echo [SINAL MASTER: PURIFICACAO DE FASE]
echo Sincronizando estúdio no caminho absoluto...
cd /d "C:\Users\Pichau\Repos\MenirVital\Menir"

echo O limitador esta armado. O ruido de fundo sera extirpado.
echo O .git, o .env e a Menir_Inbox formam o Headroom intocavel.
echo Pressione CTRL+C para abortar a masterizacao ou ENTER para cortar o sinal.
pause >nul

echo.
echo [GAIN] A iniciar expurgo...

:: 1. Protecao de Fase: Ocultar o .env (caso nao esteja) para o loop ignorar
if exist .env attrib +h .env

:: 2. Expurgo de Ficheiros Soltos
echo Limpando frequencias parasitas na raiz...
for %%I in (*.*) do (
    if /I not "%%I"=="purifica_menir.bat" (
        if /I not "%%I"==".env" (
            del /F /Q "%%I"
        )
    )
)

:: 3. Expurgo de Diretorios (O Colapso do Legado)
echo Incinerando canais mortos e diretorios defasados...
for /D %%D in (*) do (
    if /I not "%%D"==".git" (
        if /I not "%%D"=="Menir_Inbox" (
            rmdir /S /Q "%%D"
        )
    )
)

:: 4. Restauracao de Fase
if exist .env attrib -h .env

echo.
echo [0dB] O silencio foi estabelecido. O disco magnetico esta virgem.
echo Aguardando o Arquiteto sinalizar para a gravacao do Take 1.
pause