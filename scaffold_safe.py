#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scaffold seguro para o repositório Menir.

- Cria templates de documentação e stubs apenas se não existirem.
- Não faz commit automático; evita sobrescrever arquivos reais.
"""

import os
from pathlib import Path

README_TEMPLATE = """# Menir — Projeto Grafo “Livro Débora”

## 🚀 Visão Geral  
Menir é o sistema de gerenciamento de grafo narrativo para a obra **Livro Débora**. Ele utiliza Neo4j como backend, com um schema canônico para capítulos, cenas, eventos, personagens, lugares e metadados de versionamento, hash de integridade, auditoria e logs. Este repositório contém toda a infraestrutura para: ingestão de conteúdo (JSON, texto, PDF), manutenção do grafo, auditoria de integridade, exportação de relatórios e automação via CI/CD — tudo versionado e rastreável.

## 📂 Estrutura do Repositório (Template)

/menir
├── artifacts/ # Fonte da verdade (JSONs, PDFs, textos, etc.)
├── scripts/ # Scripts de operação (clean, ingest, rebuild, audit, seed, etc.)
├── docs/ # Documentação formal (modelagens, especificações, pipeline spec)
│   └── DATA_PIPELINE_SPEC.md
├── .github/workflows/ # Workflows de automação (CI/CD)
├── reports/ # Resultados de auditoria (CSVs, logs, etc.)
├── schema/ # Modelo de grafo, contratos, instruções de schema
├── requirements.txt # Dependências Python
└── README.md # (Este arquivo, template)

## ✅ Funcionalidades do Menir (resumo)  
- Ingestão estruturada, versionamento de capítulos, auditoria de integridade  
- Exportação de relatórios, pipeline automatizado, isolamento de dados  
- Rastreabilidade, logs, histórico de versões  

## 🛠️ Como usar (modo desenvolvimento)

```bash
# Exemplos de comandos típicos (ajuste aos scripts reais existentes):
# python scripts/clean_all.py
# python scripts/rebuild_and_ingest_debora.py
# python scripts/audit_export_csv.py --output-dir=reports
# Abra o Neo4j e verifique o grafo / relatórios CSV
```
"""

SCRIPT_STUBS = {
    "scripts/clean_all.py": "# stub clean_all.py — limpar grafo\n",
    "scripts/rebuild_and_ingest_debora.py": "# stub rebuild_and_ingest_debora.py — ingresso de dados\n",
    "scripts/audit_export_csv.py": "# stub audit_export_csv.py — auditoria e exportação CSV\n",
    "scripts/schema_report.py": "# stub schema_report.py — relatório de labels/rels\n",
}


def ensure_dirs() -> None:
    Path("scripts").mkdir(parents=True, exist_ok=True)
    Path("docs").mkdir(parents=True, exist_ok=True)


def write_readme_template() -> None:
    target = Path("README.md")
    if target.exists():
        print("README.md já existe — criando README.template.md em vez de sobrescrever.")
        target = Path("README.template.md")
    target.write_text(README_TEMPLATE, encoding="utf-8")
    print(f"Template de README gravado em: {target}")


def write_stub_files() -> None:
    for path_str, content in SCRIPT_STUBS.items():
        path = Path(path_str)
        if path.exists():
            print(f"Já existe: {path}, não sobrescrevendo.")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"Stub criado: {path}")


def main() -> None:
    print("Iniciando scaffold seguro do Menir...")
    ensure_dirs()
    write_readme_template()
    write_stub_files()
    print("Scaffold concluído. Revise os arquivos gerados e insira conteúdos reais quando apropriado.")


if __name__ == "__main__":
    main()
