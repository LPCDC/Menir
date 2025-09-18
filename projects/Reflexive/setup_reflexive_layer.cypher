// ==========================
// Menir Reflexive Layer - SEED MÍNIMO
// Cria constraints + 1 exemplo real
// ==========================

// Constraints (id/únicos)
CREATE CONSTRAINT reflexao_id IF NOT EXISTS
FOR (r:Reflexao) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT tarefa_id IF NOT EXISTS
FOR (t:Tarefa) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT problema_desc IF NOT EXISTS
FOR (p:Problema) REQUIRE p.descricao IS UNIQUE;
CREATE CONSTRAINT solucao_desc IF NOT EXISTS
FOR (s:Solucao) REQUIRE s.descricao IS UNIQUE;
CREATE CONSTRAINT sugestao_desc IF NOT EXISTS
FOR (sg:Sugestao) REQUIRE sg.descricao IS UNIQUE;
CREATE CONSTRAINT parametro_nome IF NOT EXISTS
FOR (pa:Parametro) REQUIRE pa.nome IS UNIQUE;

// ------- SEED DE EXEMPLO (Itaú CSV público) -------
MERGE (t:Tarefa {id: "itau_csv_2025-09-19"})
  ON CREATE SET t.nome = "Ingestão Itaú (CSV público)"

MERGE (r:Reflexao {id: "ref_001"})
  ON CREATE SET r.data = datetime(),
                r.contexto = "Projeto Itaú - erro ExternalResource e correção com GitHub Pages",
                r.duracao = 3200,
                r.tentativas = 3

MERGE (p:Problema {descricao: "CSV inacessível no Aura (repo privado)", categoria: "acesso"})
MERGE (s:Solucao  {descricao: "Publicar via GitHub Pages / repo público", tipo: "workaround"})
MERGE (sg:Sugestao{descricao: "Automatizar criação/commit de CSV com .bat", prioridade: "alta"})
MERGE (pa:Parametro {nome: "reasoning_effort"})
  ON CREATE SET pa.valor_anterior = "rápido", pa.valor_novo = "intermediário"

MERGE (t)-[:GEROU]->(r)
MERGE (r)-[:IDENTIFICOU]->(p)
MERGE (r)-[:RESOLVEU_COM]->(s)
MERGE (r)-[:SUGERIU]->(sg)
MERGE (r)-[:AJUSTOU]->(pa);

// Confirmações rápidas
MATCH (r:Reflexao) RETURN r.id, r.contexto, r.tentativas LIMIT 5;
MATCH (r:Reflexao)-[:AJUSTOU]->(p:Parametro) RETURN p.nome, p.valor_anterior, p.valor_novo, r.contexto, r.data ORDER BY r.data DESC LIMIT 5;
MATCH (r:Reflexao)-[:SUGERIU]->(s:Sugestao) RETURN s.descricao, s.prioridade LIMIT 5;
MATCH (r:Reflexao)-[:IDENTIFICOU]->(p:Problema) RETURN p.categoria, count(*) AS freq ORDER BY freq DESC;
