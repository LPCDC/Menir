// ======================================
// Menir - Gato Mia Dashboard Seed
// ======================================

// Trigger principal
MERGE (t:Trigger {nome:"Gato Mia"})
  SET t.ativo = true,
      t.resposta = "Miau! 🐾 Dashboard completo do Menir carregado.";

// Painel de Projetos e Checkpoints
MATCH (p:Projeto)-[:TEM]->(c:Checkpoint)
OPTIONAL MATCH (p)-[:RELACIONADO_COM]->(d:Documento)
RETURN p.nome AS Projeto,
       p.ultimo_checkpoint AS UltimoCheckpoint,
       count(c) AS TotalCheckpoints,
       collect(d.nome) AS Documentos
ORDER BY Projeto;

// Alertas (sem checkpoint recente)
MATCH (p:Projeto)
WHERE p.ultimo_checkpoint < date() - duration('P7D')
RETURN p.nome AS Projeto, p.ultimo_checkpoint;
