MERGE (d3:Document {id:"governanca_liblabs_v0_1"})
SET d3.title = "Governança e Checklist de Riscos – LibLabs",
    d3.version = "v0.1",
    d3.date_published = date("2025-09-23"),
    d3.tags = ["Governanca","Riscos","LibLabs","IA"];

MERGE (org:Organization {id:"LibLabs"})
MERGE (org)-[:PUBLISHED]->(d3)
MERGE (d3)-[:PART_OF]->(org);
