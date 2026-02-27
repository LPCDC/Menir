// ======================================
// Menir - Gato Mia Dashboard
// ======================================

// Heartbeat: garante que o trigger existe
MERGE (t:Trigger {nome:"Gato Mia"})
  SET t.ativo = true,
      t.resposta = "Miau! 🐾 Dashboard completo do Menir carregado.";

// Painel principal: todos os projetos com checkpoints e documentos
MATCH (p:Projeto)-[:TEM]->(c:Checkpoint)
OPTIONAL MATCH (p)-[:RELACIONADO_COM]->(d:Documento)
RETURN p.nome AS Projeto,
       p.ultimo_checkpoint AS UltimoCheckpoint,
       count(c) AS TotalCheckpoints,
       collect(d.nome) AS Documentos
ORDER BY Projeto;

// Projetos sem checkpoint recente (< 7 dias)
MATCH (p:Projeto)
WHERE p.ultimo_checkpoint < date() - duration('P7D')
RETURN p.nome AS Projeto, p.ultimo_checkpoint;
