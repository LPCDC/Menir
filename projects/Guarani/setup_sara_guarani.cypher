// ======================================
// Menir Judicial - Setup Sara Guarani
// ======================================

// Relaciona Partes e Documentos
LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/LPCDC/Menir/main/projects/Guarani/sara_guarani.csv" AS row
MERGE (p:Parte {id: row.locador_id})
MERGE (d:Documento {id: row.doc_id})
MERGE (p)-[:RELACIONADO_A]->(d);

// Relaciona Contratos
LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/LPCDC/Menir/main/projects/Guarani/sara_guarani.csv" AS row
MERGE (c:Contrato {id: row.contrato_id})
  ON CREATE SET c.inicio = date(row.inicio), c.fim = date(row.fim), c.valor = toFloat(row.valor)
WITH row, c
MERGE (locador:Parte {id: row.locador_id})
MERGE (locatario:Parte {id: row.locatario_id})
MERGE (locador)-[:LOCADOR]->(c)
MERGE (locatario)-[:LOCATARIO]->(c);

// Auditoria: contratos por Parte
MATCH (p:Parte)-[:LOCADOR|:LOCATARIO]->(c:Contrato)
RETURN p.id AS Parte, collect(c.id) AS Contratos
LIMIT 10;

// Auditoria: maiores valores
MATCH (c:Contrato)
RETURN c.id, c.valor
ORDER BY c.valor DESC
LIMIT 10;
