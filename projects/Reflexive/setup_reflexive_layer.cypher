// ======================================
// Menir Reflexive Layer — Setup (seed mínimo)
// ======================================

// Constraints básicas (id/únicos)
CREATE CONSTRAINT reflexao_id IF NOT EXISTS FOR (r:Reflexao) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT tarefa_id   IF NOT EXISTS FOR (t:Tarefa)   REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT problema_desc IF NOT EXISTS FOR (p:Problema) REQUIRE p.descricao IS UNIQUE;
CREATE CONSTRAINT solucao_desc  IF NOT EXISTS FOR (s:Solucao)  REQUIRE s.descricao IS UNIQUE;
CREATE CONSTRAINT sugestao_desc IF NOT EXISTS FOR (sg:Sugestao) REQUIRE sg.descricao IS UNIQUE;
CREATE CONSTRAINT parametro_nome IF NOT EXISTS FOR (pa:Parametro) REQUIRE pa.nome IS UNIQUE;

// Seed exemplificativo (idempotente)
MERGE (t:Tarefa {id:"itau_csv_2025-09-19"})
  ON CREATE SET
    t.nome  = "Ingestão Itaú (CSV público)",
    t.frase = "Seed inicial de ingestão"
  ON MATCH SET
    t.frase = coalesce(t.frase, ""); // garante a propriedade

MERGE (pa:Parametro {nome:"reasoning_efo"}) ON CREATE SET pa.valor="rápido";
MERGE (pa2:Parametro {nome:"reasoning_effo"}) ON CREATE SET pa2.valor="intermediário"; // caso digitação anterior

// Exemplo de Reflexão + Sugestão + Ajuste (sem duplicar)
WITH dateTime() AS agora
MERGE (r:Reflexao {id:"refl-" + toString(timestamp())})
  ON CREATE SET r.data = agora, r.contexto = "Projeto Itaú — ajuste inicial", r.nivel="mínimo";

MERGE (s:Sugestao {descricao:"Automatizar CI para dashboard", prioridade:"alta"});
MERGE (r)-[:SUGERIU]->(s);

MERGE (p:Parametro {nome:"reasoning_effo"})
  ON CREATE SET p.valor_anterior = "rápido", p.valor_novo = "intermediário", p.valor="intermediário"
  ON MATCH SET  p.valor_anterior = coalesce(p.valor_anterior, p.valor),
                p.valor_novo      = "intermediário",
                p.valor           = "intermediário";

MERGE (r)-[:AJUSTOU]->(p);
