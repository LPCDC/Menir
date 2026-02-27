#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificação de dependências para o projeto Menir.

Executa uma checagem simples para saber se os pacotes essenciais
estão disponíveis no ambiente atual.
"""

import importlib
import sys

REQUIRED_PACKAGES = [
    "neo4j",
    # adicione/descomente outros pacotes conforme necessidade
    # "pandas",
    # "python-dotenv",
    # "requests",
    # "flask",
]


def check_package(pkg_name: str) -> bool:
    try:
        importlib.import_module(pkg_name)
        return True
    except ImportError:
        return False


def main() -> None:
    print("🔧 Verificando dependências do ambiente Menir...\n")
    missing = []
    for pkg in REQUIRED_PACKAGES:
        if check_package(pkg):
            print(f"✔ OK  — pacote '{pkg}' está instalado.")
        else:
            print(f"✘ FALTA — pacote '{pkg}' NÃO está instalado.")
            missing.append(pkg)

    if missing:
        print("\n⚠️ Algumas dependências estão faltando:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nPara instalar, rode:\n")
        print("    pip install " + " ".join(missing))
        sys.exit(1)

    print("\n✅ Todas dependências verificadas. Ambiente OK.")


if __name__ == "__main__":
    main()