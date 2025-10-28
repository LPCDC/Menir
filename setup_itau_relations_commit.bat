// ======================================
// Menir Judicial - Setup Itaú Relations
// ======================================

// Relaciona Partes e Documentos (pelo campo parte_id)
LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/LPCDC/Menir/main/projects/Itau/itau_documentos.csv" AS row
MATCH (p:Parte {id: row.parte_id})
MATCH (d:Documento {id: row.doc_id})
MERGE (p)-[:RELACIONADO_A]->(d);

// Relaciona Contas e Transacoes (pelo campo conta_id)
LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/LPCDC/Menir/main/projects/Itau/itau_transacoes.csv" AS row
MATCH (c:Conta {id: row.conta_id})
MATCH (t:Transacao {id: row.transacao_id})
MERGE (c)-[:REGISTRA]->(t);

// Auditoria simples: checa se Partes têm Documentos
MATCH (p:Parte)-[:RELACIONADO_A]->(d:Documento)
RETURN p.nome AS Parte, collect(d.nome) AS Documentos
LIMIT 10;

// Auditoria simples: transacoes de maior valor
MATCH (t:Transacao)
RETURN t.id, t.valor
ORDER BY t.valor DESC
LIMIT 10;
