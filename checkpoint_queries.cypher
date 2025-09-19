// ================================
// MENIR — CheckPoint Queries
// ================================

// 1. Listar todos os triggers ativos
MATCH (t:Trigger)
RETURN t.nome AS Trigger, t.ativo AS Ativo, t.resposta AS Resposta, t.data_registro AS Desde
ORDER BY t.nome;

// 2. Verificar gatilhos específicos
MATCH (t:Trigger)
WHERE t.nome IN ["Marco", "Eco", "Gato Mia"]
RETURN t.nome, t.resposta, t.ativo;

// 3. Conferir parâmetros reflexivos ajustados
MATCH (p:Parametro)<-[:AJUSTOU]-(r:Reflexao)
RETURN p.nome, p.valor_anterior, p.valor_novo, r.contexto, r.data
ORDER BY r.data DESC;

// 4. Sugestões registradas
MATCH (r:Reflexao)-[:SUGERIU]->(s:Sugestao)
RETURN s.descricao, s.prioridade
ORDER BY s.prioridade DESC;

// 5. Problemas identificados
MATCH (r:Reflexao)-[:IDENTIFICOU]->(p:Problema)
RETURN p.categoria, count(*) AS freq
ORDER BY freq DESC;

// 6. Sanity check — contar entidades principais
CALL {
  MATCH (p:Projeto) RETURN count(p) AS projetos
}
CALL {
  MATCH (t:Trigger) RETURN count(t) AS triggers
}
CALL {
  MATCH (p:Parametro) RETURN count(p) AS parametros
}
RETURN projetos, triggers, parametros;
