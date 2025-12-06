# Menir — Projeto Grafo “Livro Débora”

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
