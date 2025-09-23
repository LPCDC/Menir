MATCH (d:Document {id:"aia_ai_spec_2024"})<-[:CITED_IN]-(c:Claim)
RETURN d.title AS documento, c.text AS claim, c.status AS status;
