/* claims_ingest.cypher — para documentos como o AIA 2024 */
MERGE (d:Document {id:"aia_ai_spec_2024"})
SET d.title="The Architect’s Journey to Specification – AI in Architecture",
    d.publisher="AIA",
    d.date_published=date("2024-11-01"),
    d.source_type="report",
    d.tags=["AEC","AI","Specification"];

UNWIND [
  {text:"Adoção liderada por firmas grandes", status:"confirmed"},
  {text:"Baixa adoção em tarefas críticas (spec/custos/listas)", status:"confirmed"},
  {text:"Alta demanda por educação/ética/segurança", status:"confirmed"}
] AS c
MERGE (cl:Claim {text:c.text})
SET cl.status=c.status
MERGE (cl)-[:CITED_IN]->(d);
