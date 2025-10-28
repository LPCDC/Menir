// Diagnóstico limpo

MATCH (d:Document)
RETURN d.id AS id, d.title AS title
LIMIT 10;

MATCH (c:Claim)
RETURN c.text AS claim, c.status AS status
LIMIT 10;

MATCH ()-[:CITED_IN]->()
RETURN count(*) AS qtd_rel_cited_in;

MATCH (d:Document {id:"aia_ai_spec_2024"})
OPTIONAL MATCH (c:Claim)-[:CITED_IN]->(d)
RETURN d.title AS document, collect(c.text) AS linked_claims;
