////////////////////////////////////////////////////////////////////////
// Validate Relações Itaú
////////////////////////////////////////////////////////////////////////

// Verificar transações que deveriam referenciar Documento, mas não têm
MATCH (t:Transacao)
WHERE t.id IS NOT NULL
  AND t.doc_id IS NOT NULL AND trim(t.doc_id) <> ""
  AND NOT (t)-[:REFERE_A]->(:Documento)
RETURN "Sem Documento" AS tipoProblema, t.id AS transacao_id, t.doc_id AS doc_id
LIMIT 20;

// Verificar transações que deveriam envolver Parte, mas não têm
MATCH (t:Transacao)
WHERE t.id IS NOT NULL
  AND t.parte_id IS NOT NULL AND trim(t.parte_id) <> ""
  AND NOT (t)-[:ENVOLVENDO]->(:Parte)
RETURN "Sem Parte" AS tipoProblema, t.id AS transacao_id, t.parte_id AS parte_id
LIMIT 20;

// Verificação geral de contagens
MATCH (n) RETURN labels(n)[0] AS label, count(*) AS total ORDER BY total DESC LIMIT 10;

// Amostras de relacionamentos existentes
MATCH (t:Transacao)-[:REFERE_A]->(d:Documento)
RETURN t.id AS transacao_id, d.id AS documento_id LIMIT 10;

MATCH (t:Transacao)-[:ENVOLVENDO]->(p:Parte)
RETURN t.id AS transacao_id, p.id AS parte_id LIMIT 10;
