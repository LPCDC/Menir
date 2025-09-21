// Exemplos de limpeza (revisão manual recomendada)
// 1) Marcar duplicados exatos como near-dup (para revisão)
MATCH (a:Documento),(b:Documento)
WHERE a.sha256 = b.sha256 AND a.id < b.id
MERGE (a)-[:NEAR_DUPLICATE_OF]->(b);

// 2) Deletar rótulos temporários/antigos se existirem (ajuste conforme necessário)
// MATCH (n:`Transação`) REMOVE n:`Transação` SET n:Transacao;

// 3) Remover relações quebradas (se necessário) — use com cautela
// MATCH ()-[r]->() WHERE NOT EXISTS(r.uid) AND type(r) IN ['REFERE_A','ENVOLVENDO'] DELETE r;
