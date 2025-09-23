// projects/Otani/ingest.cypher
MERGE (d:Document {id:"otani_booklet_v1"})
SET d.title = "Otani Booklet Draft",
    d.source_type = "render_project",
    d.date_published = date("2025-09-23"),
    d.tags = ["Render","Otani","LibLabs"]

WITH d
UNWIND [
  {text:"Altar budista como foco narrativo", status:"draft"},
  {text:"Estilo escandinavo-industrial definido", status:"confirmed"},
  {text:"Renderização MyArchitect usada como base", status:"confirmed"}
] AS claimData
MERGE (c:Claim {text:claimData.text})
SET c.status = claimData.status
MERGE (c)-[:CITED_IN]->(d);
