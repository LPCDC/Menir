// claims_ingest_final.cypher
// Ingest + fix com matching tolerante a case / espaços / variações

// 1. Encontrar ou criar o Document corretamente
MERGE (d:Document)
  // tolerância: lowercase id e trim
  // se já houver documento com id igual ignorando case ou espaços, usamos esse
  // mas Neo4j não permite MERGE em função, então usamos MATCH primeiro, depois MERGE fallback

WITH d

// Primeiro tentar MATCH tolerante
MATCH (d0:Document)
WHERE toLower(trim(d0.id)) = toLower(trim("aia_ai_spec_2024"))
WITH d0
// Se encontrar, redefine d para esse nodo
SET d = d0

// Caso não exista, criar novo com MERGE
MERGE (doc:Document {id:"aia_ai_spec_2024"})
ON CREATE SET doc.title = "The Architect’s Journey to Specification – AI in Architecture",
              doc.publisher = "AIA",
              doc.date_published = date("2024-11-01"),
              doc.source_type = "report",
              doc.tags = ["AEC","AI","Specification"]
WITH doc AS document

// 2. Garantir os Claims são criados/atualizados
UNWIND [
  {text:"Adoção liderada por firmas grandes", status:"confirmed"},
  {text:"Baixa adoção em tarefas críticas (spec/custos/listas)", status:"confirmed"},
  {text:"Alta demanda por educação/ética/segurança", status:"confirmed"}
] AS c
MERGE (cl:Claim {text:c.text})
SET cl.status = c.status
WITH document, cl

// 3. Criar relacionamento se não existir
MERGE (cl)-[:CITED_IN]->(document);
