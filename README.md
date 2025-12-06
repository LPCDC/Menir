# Menir – Development Container (v10.4.1)

> Este repositório abriga a camada pseudo-OS **Menir**. Este codespace / devcontainer configura um ambiente de desenvolvimento isolado e reprodutível.

## 📦 Setup

1. Abra o repositório no GitHub.  
2. Clique em **Code → Codespaces → Create codespace on main**.  
3. O container será inicializado com:  
   - Python 3.12  
   - Docker-in-Docker  
   - Extensões: Python, Pylance, Docker  
4. (Opcional) Para rodar Neo4j local dentro do container:
   ```bash
   docker-compose up -d
   ```

---

## Propósito
Branch **principal e estável** do Menir.  
Aqui vive o código consolidado após testes nas branches `boot` e `boot-local`.

## Estrutura do Projeto
- `/core` — módulos de memória, LGPD, zk-log, ingest  
- `/projects` — subprojetos (Itaú, Tivoli, Iberê, etc.)  
- `/graph` — scripts Neo4j / Cypher  
- `/docs` — documentação técnica e relatórios  
- `/logs` — auditorias de boot e ingestão  

## Instalação
```bash
git clone https://github.com/LPCDC/Menir.git
cd Menir
git checkout main
conda activate menir
pip install -r requirements.txt
```

## 📊 Automatic Snapshot (CI)

Este repositório está configurado com workflow GitHub Actions para gerar snapshots de estado diariamente.

**Schedule:** Daily at 03:00 UTC (00:00 BRT / 22:00 EST)

Para gerar snapshot manualmente, execute:

```bash
source .venv/bin/activate
python scripts/generate_state_snapshot.py
```

Ou use a versão leve:

```bash
python scripts/quick_snapshot.py
```

Snapshots são versionados com tags no formato `snapshot-YYYY-MM-DDTHH:MM:SSZ` para auditoria.

## Menir-10 (local psych engine)

Menir-10 is a lightweight "psych engine" that logs interactions locally to JSONL and can export to Neo4j via Cypher. It requires only Python stdlib and provides:

- **Local logging**: Interactions are stored in `logs/menir10_interactions.jsonl` with rich metadata.
- **Neo4j export**: Generate Cypher `CREATE` statements for graph import.
- **Insights CLI**: Query projects, generate summaries, and render GPT-ready context blocks.
- **Boot instrumentation**: Optional integration with `scripts/boot_now.py` via `MENIR_PROJECT_ID` env var.

For safe experimentation without touching real data, use the synthetic test project `test_menir10` as documented in [docs/PROJECT_TEST_MENIR10.md](docs/PROJECT_TEST_MENIR10.md).

See [docs/MENIR10_OVERVIEW.md](docs/MENIR10_OVERVIEW.md) and [docs/MENIR10_LOG_SCHEMA.md](docs/MENIR10_LOG_SCHEMA.md) for more details.
```
