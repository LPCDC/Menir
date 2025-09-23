// claims_ingest_final_diagnose.cypher

// 1. Verificar se existe Document com id exato, case-sensitive/spaces
MATCH (d:Document {id:"aia_ai_spec_2024"})
RETURN count(d) AS exact_match_count, properties(d) AS exact_match_props;

// 2. Verificar se existe Document com id parecido ignorando case ou espaços
MATCH (d:Document)
WHERE toLower(trim(d.id)) = toLower(trim("aia_ai_spec_2024"))
RETURN count(d) AS case_insensitive_count, d.id AS matched_id, properties(d) AS matched_props;

// 3. Verificar Claims que deveriam estar ligados (todos ou parte) e ver se existem
UNWIND [
  "Adoção liderada por firmas grandes",
  "Baixa adoção em tarefas críticas (spec/custos/listas)",
  "Alta demanda por educação/ética/segurança"
] AS textClaim
MATCH (c:Claim {text: textClaim})
RETURN textClaim AS claim_text, properties(c) AS claim_props;

// 4. Verificar relacionamentos CITED_IN para esse document com tolerância
MATCH (c:Claim)-[:CITED_IN]->(d:Document)
WHERE toLower(trim(d.id)) = toLower(trim("aia_ai_spec_2024"))
RETURN c.text AS linked_claim, d.id AS doc_id;

// 5. Se faltar relacionamento, criar para teste
MATCH (d0:Document)
WHERE toLower(trim(d0.id)) = toLower(trim("aia_ai_spec_2024"))
WITH d0 AS document

UNWIND [
  {text:"Adoção liderada por firmas grandes", status:"confirmed"},
  {text:"Baixa adoção em tarefas críticas (spec/custos/listas)", status:"confirmed"},
  {text:"Alta demanda por educação/ética/segurança", status:"confirmed"}
] AS cDef
MERGE (cl:Claim {text:cDef.text})
SET cl.status = cDef.status
MERGE (cl)-[:CITED_IN]->(document);

RETURN "Done test ingest" AS status;
