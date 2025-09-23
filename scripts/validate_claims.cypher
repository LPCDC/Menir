/* validate_claims.cypher */
MATCH (d:Document {id:"aia_ai_spec_2024"})<-[:CITED_IN]-(c:Claim)
RETURN d.title, c.text, c.status;
