////////////////////////////////////////////////////////////////////////
// Gatomia — Status consolidado (JSON)
// Saída única: {labels:[], rels:[], projetos:[], alerts:[]}
////////////////////////////////////////////////////////////////////////
CALL {
  MATCH (n)
  UNWIND labels(n) AS label
  WITH label, count(*) AS nodes
  ORDER BY nodes DESC
  RETURN collect({label: label, nodes: nodes}) AS labels
}
CALL {
  MATCH ()-[r]->()
  WITH type(r) AS rel, count(*) AS total
  ORDER BY total DESC
  RETURN collect({rel: rel, total: total}) AS rels
}
CALL {
  MATCH (p:Projeto)
  WITH p,
       [x IN [
         CASE WHEN p.slug IS NULL THEN 'slug ausente' END,
         CASE WHEN p.nome IS NULL THEN 'nome ausente' END,
         CASE WHEN p.ativo IS NULL THEN 'ativo indefinido' END
       ] WHERE x IS NOT NULL] AS inconsistencias
  WITH collect({
    slug: p.slug, nome: p.nome,
    ativo: coalesce(p.ativo,false),
    status: p.status, updatedAt: p.updatedAt,
    inconsistencias: inconsistencias
  }) AS projetos
  RETURN projetos
}
CALL {
  MATCH (n:`Transação`) RETURN count(n) AS legado
}
WITH labels, rels, projetos, legado
WITH labels, rels, projetos,
     (CASE WHEN legado > 0
           THEN ['Restam '+toString(legado)+' nós com label `Transação` (com acento).']
           ELSE [] END) AS alerts
RETURN {labels: labels, rels: rels, projetos: projetos, alerts: alerts} AS status;
