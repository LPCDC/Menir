#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_dependencies_local.py — Verificação simples de dependências para Menir (modo local / permissivo).

Testa apenas presença dos pacotes listados em REQUIRED_PACKAGES.
Se algum estiver faltando, avisa e retorna exit code 1.
"""

import importlib
import sys

REQUIRED_PACKAGES = [
    "neo4j",
    # adicione aqui outros pacotes conforme presença nos seus scripts:
    # ex: "pandas", "python-dotenv", "requests", etc.
]


def check_pkg(pkg_name: str) -> bool:
    try:
        importlib.import_module(pkg_name)
        return True
    except ImportError:
        return False


def main() -> None:
    print("🔧 Verificando dependências do ambiente (modo local / permissivo)...\n")
    missing = []
    for pkg in REQUIRED_PACKAGES:
        if check_pkg(pkg):
            print(f"✔ OK — pacote '{pkg}' está instalado.")
        else:
            print(f"✘ FALTA — pacote '{pkg}' NÃO está instalado.")
            missing.append(pkg)

    if missing:
        print("\n⚠️ Dependências faltando:")
        for p in missing:
            print(f"   - {p}")
        print("\nPara instalar, rode:\n    pip install " + " ".join(missing))
        sys.exit(1)

    print("\n✅ Todas dependências mínimas presentes.")


if __name__ == "__main__":
    main()
