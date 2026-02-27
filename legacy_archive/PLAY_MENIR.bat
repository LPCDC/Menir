@echo off
echo 🎸 Preparando o som do Menir...
:: Instala a biblioteca estável
pip install google-generativeai neo4j --upgrade
echo 🎚️ Rodando o Menir Bridge...
python menir_bridge.py
pause