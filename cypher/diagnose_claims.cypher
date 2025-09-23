// 1. Verificar documentos existentes
MATCH (d:Document) 
RETURN d.id AS id, d.title AS title
LIMIT 10;

// 2. Verificar claims existentes
MATCH (c:Claim) 
RETURN c.text AS claim, c.status AS status
LIMIT 10;

// 3. Verificar quantidade de relacionamentos CITED_IN
MATCH ()-[:CITED_IN]->() 
RETURN count(*) AS qtd_rel_cited_in;

// 4. Verificar relações específicas do documento alvo
MATCH (d:Document {id:"aia_ai_spec_2024"})
OPTIONAL MATCH (c:Claim)-[:CITED_IN]->(d)
RETURN d.title AS document, collect(c.text) AS linked_claims;
