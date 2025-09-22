////////////////////////////////////////////////////////////////////////
// Export CSV — Gatomia
// Gera nodes.csv e rels.csv para import externo
////////////////////////////////////////////////////////////////////////

// Exportar nós
CALL apoc.export.csv.all("nodes.csv", {
  useTypes:true,
  store:true,
  nodesOfRelationships:true
});

// Exportar relacionamentos
CALL apoc.export.csv.all("rels.csv", {
  useTypes:true,
  store:true,
  onlyRelationships:true
});
