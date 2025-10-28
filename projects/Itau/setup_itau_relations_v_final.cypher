////////////////////////////////////////////////////////////////////////
// Transações + Relações – versão que preserva scope de row
////////////////////////////////////////////////////////////////////////
LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/LPCDC/Menir/main/projects/Itau/itau_transacoes.csv" AS row
WITH row
WHERE 
  row.id IS NOT NULL AND trim(row.id) <> "" AND
  row.doc_id IS NOT NULL AND trim(row.doc_id) <> "" AND
  row.parte_id IS NOT NULL AND trim(row.parte_id) <> ""

MERGE (t:Transacao {id: row.id})
  ON CREATE SET
    t.valor = toFloat(row.valor),
    t.data  = row.data,
    t.tipo  = row.tipo
  ON MATCH SET
    t.atualizado_em = timestamp()

// Agora garantir row no WITH
WITH t, row

// Relação com Documento
MATCH (d:Documento {id: row.doc_id})
WITH t, row, d
MERGE (t)-[:REFERE_A]->(d)

// Relação com Parte
WITH t, row
MATCH (p:Parte {id: row.parte_id})
WITH t, p
MERGE (t)-[:ENVOLVENDO]->(p);
