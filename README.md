# Menir (MenirVital)

> **Branch Única**: Este projeto segue a política de **branch única (`main`)**.  
> Features devem ser desenvolvidas em branches temporárias e mergeadas via PR ou merge direto após testes.

## 🛠️ Automação e Uso

O projeto conta com um `Makefile` e scripts em `scripts/` para tarefas comuns.

### Pré-requisitos
*   **Python 3.10+** (com dependências no `requirements.txt`)
*   **Neo4j Desktop** ou **AuraDB** rodando.
*   Arquivo `.env` na raiz com credenciais (veja `.env.example`).
*   (Opcional) **Make** (no Windows via `choco install make`).

### Comandos Principais

| Comando | Descrição |
| :--- | :--- |
| `make healthcheck` | Testa conectividade com o Neo4j. |
| `make backup` | Cria tag Git de backup e sobe para o remote. |
| `make ingest` | Roda pipeline de ingestão de dados. |
| `make clean-logs` | Remove logs com mais de 30 dias. |
| `make full-cycle` | Executa Healthcheck → Ingest → Backup → Clean. |
| `make dump-graph` | (Placeholder) Exporta snapshot do banco. |

---

[![Dependências OK](https://img.shields.io/badge/dependencies-checked-brightgreen.svg)](scripts/check_dependencies_local.py)

## 🚀 Visão Geral
O Menir é o sistema de gerenciamento de grafo narrativo para a obra “Livro Débora”. Ele utiliza Neo4j como backend, com schema canônico para capítulos, cenas, eventos, personagens, lugares e camadas de metadados (versões, hash de integridade, histórico, auditoria). Este repositório contém infraestrutura para ingestão, manutenção do grafo, auditoria de integridade e exportação de relatórios, de modo versionado e rastreável.

### Por que este projeto existe
- Controle de versões literárias em grafo, com histórico e hashes de origem.
- Análises estruturadas: rede de personagens, sequência narrativa, integridade de cenas/eventos, relações e detecção de “gaps”.
- Pipeline auditável e repetível: ingestão → auditoria → export → versionamento.

---

## 📂 Estrutura do Repositório

```
/Menir
├── rebuild_and_ingest_debora.py     # aplica schema + ingestão do Cap.1
├── audit_export_csv.py              # auditoria + exportação de relatórios CSV
├── clean_menir_grafo.sh             # limpeza de nós fora do schema
├── schema_report.py                 # relatório de labels/relationships atuais
├── setup_livro_debora_schema.py     # cria constraints/indexes do schema
├── cypher/                          # scripts Cypher auxiliares
├── data/                            # insumos de ingestão
├── docs/                            # documentação técnica
├── exports/                         # saídas (CSVs, snapshots)
├── logs/                            # logs e auditorias
├── scripts/                         # utilitários adicionais (snapshots, CI)
├── templates/                       # modelos e metadados
└── requirements.txt
```

---

## ✅ Funcionalidades Principais
- Ingestão estruturada criando nós `Work`, `Chapter`, `ChapterVersion`, `Scene`, `Event`, `Character`, `Place`, etc.
- Versionamento de capítulos com histórico e hashes de origem.
- Auditoria de integridade: cenas sem eventos, personagens órfãos, contagens, co-aparecimentos e relações entre personagens.
- Exportação de relatórios CSV para análise externa.
- Pipeline automatizado compatível com Neo4j local ou remoto (configurável via variáveis de ambiente).

---

## 🛠️ Como executar (modo local / desenvolvimento)

Pré-requisitos: Neo4j acessível (bolt/neo4j), Python 3.11+.

Configurar credenciais (ajuste conforme o seu banco):
```bash
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=menir123
export NEO4J_DB=neo4j   # opcional; use quando o DB não for default
```

Instalar dependências:
```bash
pip install -r requirements.txt
```

Aplicar schema e ingerir o Capítulo 1:
```bash
python setup_livro_debora_schema.py
python rebuild_and_ingest_debora.py
```

Gerar auditoria e exportar relatórios CSV (diretório padrão: `exports/`):
```bash
python audit_export_csv.py --output-dir exports
```

Listar labels e tipos de relações atuais:
```bash
python schema_report.py
```

Limpar nós fora do schema canônico (cuidado: operação destrutiva, pede confirmação):
```bash
./clean_menir_grafo.sh
```

Para scripts adicionais (snapshots, sanity checks), veja `scripts/` e `docs/`.
```
