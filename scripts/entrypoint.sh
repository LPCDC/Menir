#!/bin/bash
# Menir Core V5.1 - Centralized Rack Entrypoint
# Boots the system optimally, avoiding software sprawl.

# 1. Pre-Flight Assurances
echo "[Menir Boot] Verificando integridade das pastas do container..."
mkdir -p logs
mkdir -p Menir_Inbox
mkdir -p Menir_Archive

# 2. Inicia o Motor Assíncrono Principal
echo "[Menir Boot] Acordando o Watchdog e a Synapse Control Plane..."
exec python -m src.v3.core.menir_runner
