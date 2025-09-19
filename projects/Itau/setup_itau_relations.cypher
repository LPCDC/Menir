////////////////////////////////////////////////////////////////////////
// Patch Relações Faltantes Itaú
////////////////////////////////////////////////////////////////////////

// Criar relacionamento REFERE_A para transações com documento existente
MATCH (t:Transacao), (d:Documento)
WHERE t.doc_id IS NOT NULL AND trim(t.doc_id) <> ""
  AND t.doc_id = d.id
  AND NOT (t)-[:REFERE_A]->(d)
MERGE (t)-[:REFERE_A]->(d);

// Criar relacionamento ENVOLVENDO para transações com parte existente
MATCH (t:Transacao), (p:Parte)
WHERE t.parte_id IS NOT NULL AND trim(t.parte_id) <> ""
  AND t.parte_id = p.id
  AND NOT (t)-[:ENVOLVENDO]->(p)
MERGE (t)-[:ENVOLVENDO]->(p);

// Validação pós patch
MATCH (t:Transacao)-[:REFERE_A]->(d:Documento)
RETURN t.id AS transacao_id, d.id AS documento_id LIMIT 10;

MATCH (t:Transacao)-[:ENVOLVENDO]->(p:Parte)
RETURN t.id AS transacao_id, p.id AS parte_id LIMIT 10;
