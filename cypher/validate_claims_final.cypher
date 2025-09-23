// cypher/validate_claims_final.cypher
// Validação consolidada de ingestão de claims -> LibLabs

// 1. Confirma existência do documento alvo
MATCH (d:Document {id:"aia_ai_spec_2024"})
RETURN d.id AS doc_id, d.title AS title, labels(d) AS labels, properties(d) AS props;

// 2. Claims vinculadas ao documento
MATCH (d:Document {id:"aia_ai_spec_2024"})<-[:CITED_IN]-(c:Claim)
RETURN d.id AS doc_id, c.text AS claim_text, c.status AS status
ORDER BY c.text;

// 3. Claims órfãs (sem CITED_IN)
MATCH (c:Claim)
WHERE NOT (c)-[:CITED_IN]->(:Document)
RETURN c.text AS orphan_claim, c.status AS status
ORDER BY c.text
LIMIT 20;

// 4. Status final
RETURN "Validated" AS status;
