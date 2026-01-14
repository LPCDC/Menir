#!/usr/bin/env python3
"""
env_validator.py — Environment validation utility for Menir.
Ensures PYTHON_ENV is set to a valid value before startup.
"""

import os
import sys

# Lista de ambientes permitidos
ALLOWED_ENVS = ["production", "development", "staging"]

def validate_environment():
    """Verifica se a variável de ambiente PYTHON_ENV está definida e é válida."""
    env = os.environ.get("PYTHON_ENV")
    
    if env is None:
        print("ERRO FATAL: Variável de ambiente PYTHON_ENV não definida.")
        print("Por favor, defina para um dos seguintes: " + ", ".join(ALLOWED_ENVS))
        sys.exit(1)
        
    if env not in ALLOWED_ENVS:
        print(f"ERRO FATAL: Valor '{env}' inválido para PYTHON_ENV.")
        print("Valores permitidos são: " + ", ".join(ALLOWED_ENVS))
        sys.exit(1)
        
    print(f"Ambiente validado com sucesso: {env}")
    return env

if __name__ == "__main__":
    validate_environment()
