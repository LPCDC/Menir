# Menir Functions Pack

Este pacote adiciona funções comprovadas ao Menir (compatível com Neo4j Aura):

1. **Integrity by Constraint** → índices e constraints para consistência.
2. **Energy-Aware Routing** → A* com custo de energia.
3. **Explainable Layers** → sempre retorna subgrafo justificando decisões.
4. **Blockchain Auditing** → hashing SHA-256 interno com APOC.
5. **CI com GitHub Actions** → aplica schema e importa CSV automaticamente.

## Como usar

1. Copie todo o conteúdo deste pacote para a raiz do seu repositório Menir.
2. Configure os `secrets` no GitHub do repositório:
   - `NEO4J_URI` (ex: neo4j+s://<host>:7687)
   - `NEO4J_USER`
   - `NEO4J_PASSWORD`
3. Faça commit e push. O workflow `menir-ci.yml` aplicará o `setup.cypher` no Aura.
4. Use os arquivos `.cypher` como exemplos de consultas prontas para cada função.

---
