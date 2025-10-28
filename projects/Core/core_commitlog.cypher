// MENIR Core — Commit Log Tracker
// Para cada commit aplicado no GitHub, registre no grafo MENIR.

:param {
  commit_id: "sha-or-hash",
  autor: "Seu Nome Aqui",
  msg: "gat: rename MarcoPolo → Gatomi + add dashboard",
  arquivos: ["projects/Gatomia/gatomia_dashboard.cypher", "projects/Reflexive/setup_reflexive_layer.cypher"],
  data: date()
}

MERGE (c:Commit {id:$commit_id})
ON CREATE SET
  c.msg       = $msg,
  c.autor     = $autor,
  c.data      = $data,
  c.arquivos  = $arquivos;

// Ligação reflexiva: cada commit vira uma reflexão de evolução
MERGE (r:Reflexao {id:$commit_id})
ON CREATE SET r.contexto = $msg, r.data = datetime()

MERGE (r)-[:REFLETIU]->(c);
