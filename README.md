---

### 🧩 `README.md` — `main`
```markdown
# Menir – Main
Repositório: LPCDC/Menir · Branch: main

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