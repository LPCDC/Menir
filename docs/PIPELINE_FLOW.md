# 📊 Menir Data Pipeline Flow

## Visão geral do pipeline

A ingestão e manutenção do grafo Menir segue uma sequência padronizada de etapas:

```
┌──────────────────────┐
│ 1. CLEAN / RESET     │  ← opcional, para limpar grafo antigo
└────────────┬─────────┘
             │
             ▼
┌──────────────────────┐
│ 2. SCHEMA SETUP      │  (constraints + índices)
└────────────┬─────────┘
             │
             ▼
┌──────────────────────┐
│ 3. SEED (Macro)      │  (Work, Chapters, personagens base)
└────────────┬─────────┘
             │
             ▼
┌──────────────────────┐
│ 4. INGEST (Micro)    │  (Cenas, eventos, entidades, relações)
└────────────┬─────────┘
             │
             ▼
┌──────────────────────┐
│ 5. AUDIT / EXPORT    │  (Valida grafo, exporta CSVs)
└────────────┬─────────┘
             │
             ▼
┌──────────────────────┐
│ 6. REPORT / OUTPUT   │  (Relatórios, gráficos, backup, etc.)
└──────────────────────┘
```

---

## Descrição de cada etapa

### 1. CLEAN / RESET (Opcional)

- **Quando usar**: Ao começar um rebuild completo ou ao descartar um grafo corrompido.
- **Ação**: Remove todos os nós e relações existentes.
- **Script**: `clean_all.py` ou `clean_menir_grafo.sh`
- **Cuidado**: Operação destrutiva. Pede confirmação.

### 2. SCHEMA SETUP

- **Quando usar**: Primeira execução ou após atualizar o schema.
- **Ação**: Cria constraints e índices conforme schema v2 (labels, properties, tipos de relações).
- **Script**: `setup_livro_debora_schema.py`
- **Output**: Grafo pronto com estrutura base.

### 3. SEED (Macro)

- **Quando usar**: Após schema setup, para inicializar dados estruturais.
- **Ação**: Cria nós de alto nível: `Work` (obra), `Chapter` (capítulos), personagens arquétipos, metadados iniciais.
- **Script**: Parte de `rebuild_and_ingest_debora.py` ou script dedicado.
- **Output**: Estrutura raiz do grafo preenchida.

### 4. INGEST (Micro)

- **Quando usar**: Para cada capítulo/seção de conteúdo.
- **Ação**: Lê dados de origem (JSON, PDF, texto) e cria nós de detalhe: `Scene`, `Event`, `Character`, `Place`, `Object`, etc.
- **Script**: `rebuild_and_ingest_debora.py` (com dados em `data/` ou `artifacts/`).
- **Output**: Grafo populado com cenas, eventos e entidades.

### 5. AUDIT / EXPORT

- **Quando usar**: Após ingestão, para validar e exportar.
- **Ação**: 
  - Verifica integridade: cenas sem eventos, personagens órfãos, contagens, relações inválidas.
  - Exporta relatórios CSV com estatísticas.
- **Script**: `audit_export_csv.py`
- **Output**: CSVs em `exports/` (orphan_characters.csv, scenes_without_events.csv, etc.).

### 6. REPORT / OUTPUT

- **Quando usar**: Ao final do pipeline, para documentação e backup.
- **Ação**: Gera relatórios finais, snapshots, gráficos de análise, backup do grafo.
- **Script**: `schema_report.py` (lista labels/relations) + custom export scripts.
- **Output**: Documentação, CSVs, snapshots JSON, logs.

---

## Execução prática

### Modo completo (do zero)

```bash
# 1. Verificar dependências
python scripts/check_dependencies_local.py

# 2. Limpar grafo antigo (opcional)
python clean_all.py
# ou
./clean_menir_grafo.sh

# 3. Aplicar schema
python setup_livro_debora_schema.py

# 4. Ingerir dados
python rebuild_and_ingest_debora.py

# 5. Auditar e exportar
python audit_export_csv.py --output-dir exports

# 6. Verificar labels e relations
python schema_report.py
```

### Modo incremental (add dados)

Se o schema já existe e só quer adicionar um novo capítulo:

```bash
# Pular etapas 1–3, ir direto para ingestão
python rebuild_and_ingest_debora.py --chapter 2

# Depois auditar
python audit_export_csv.py --output-dir exports
```

### Modo validação rápida

Se só quer verificar o estado atual do grafo:

```bash
python schema_report.py
```

---

## Ambiente e configuração

Antes de executar qualquer script, configure:

```bash
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=menir123
export NEO4J_DB=neo4j    # opcional
```

Ou crie um arquivo `.env` na raiz do repositório:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=menir123
NEO4J_DB=neo4j
```

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| "AuthError: Unauthorized" | Verifique NEO4J_USER, NEO4J_PASSWORD, URI. |
| "Connection refused" | Neo4j não está rodando. Inicie-o: `docker-compose up -d` ou no console Neo4j. |
| "Schema constraint already exists" | Já foi executado schema setup. Pule ou delete/recreate o banco. |
| "CSV export vazio" | Verifique se ingestão foi bem-sucedida; rode `schema_report.py` para validar grafo. |

---

## Próximos passos

- Consulte `README.md` para overview do projeto.
- Veja `DEPENDENCY_CHECKERS.md` para detalhar dependências.
- Leia `docs/MODEL.md` (se existente) para entender o schema de nós e relações.
