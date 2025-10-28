# Menir Functions Pack

Este pacote adiciona funções comprovadas ao Menir (compatível com Neo4j Aura):

1. **Integrity by Constraint** → índices e constraints para consistência.
2. **Energy-Aware Routing** → A* com custo de energia (fallback em Cypher se GDS não estiver disponível).
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

## Como rodar o grafo de teste

1. No Neo4j Aura, abra o console de queries.
2. Copie o conteúdo de `sample_graph.cypher` e clique em **Run**.
   - Isso cria os nós `A, B, C, D` e relacionamentos com `energyCost`.

## Como validar o roteamento energético (modo detalhado)

1. Copie o conteúdo de `energy_test.cypher` no console do Aura.
2. Execute o primeiro bloco:
   ```cypher
   :param { src: "A", dst: "D" }
   ```
3. Execute a query de roteamento:
   ```cypher
   MATCH p = (a:Node {id:$src})-[:REL*1..5]->(b:Node {id:$dst})
   WITH p, reduce(cost=0.0, r IN relationships(p) | cost + coalesce(r.energyCost, 1.0)) AS cost
   RETURN p AS bestPath, cost
   ORDER BY cost ASC
   LIMIT 1;
   ```
4. Resultado esperado:
   - Melhor caminho: **A → B → C → D**, custo total **8**.
   - Outros caminhos possíveis: **A → B → D** (custo 9) e **A → C → D** (custo 11).

## Como validar o roteamento energético (forma simplificada)

Se não quiser rodar `:param` e a query em dois passos separados, use o arquivo `energy_full_test.cypher`.

1. Abra o arquivo `energy_full_test.cypher` no seu editor.
2. Copie todo o conteúdo e cole no console do Neo4j Aura.
3. Clique em **Run**.
4. Resultado esperado:
   - Melhor caminho: **A → B → C → D**, custo total **8**.
   - Outros caminhos: **A → B → D** (custo 9), **A → C → D** (custo 11).

---
