// ===============================
// GatoMia / MarcoPolo Dashboard
// ===============================

// 0) Garantias leves (não quebram se já existirem)
CREATE CONSTRAINT tarefa_id IF NOT EXISTS FOR (t:Tarefa) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT parametro_nome IF NOT EXISTS FOR (p:Parametro) REQUIRE p.nome IS UNIQUE;
CREATE CONSTRAINT sugestao_desc IF NOT EXISTS FOR (s:Sugestao) REQUIRE s.descricao IS UNIQUE;
CREATE CONSTRAINT reflexao_id IF NOT EXISTS FOR (r:Reflexao) REQUIRE r.id IS UNIQUE;

// 1) Tarefas conhecidas (seed leve) – idempotente
MERGE (t:Tarefa {id:"itau_csv_2025-09-19"})
  ON CREATE SET t.nome = "Ingestão Itaú (CSV público)", t.frase = "Seed inicial de ingestão";

// 2) Checkpoint das tarefas
MATCH (t:Tarefa) RETURN t.id, t.nome, coalesce(t.frase,"") AS t_frase ORDER BY t.id;

// 3) Projetos sem checkpoint recente (< 7 dias)
OPTIONAL MATCH (p:Projeto)
WHERE exists(p.ultimo_checkpoint) AND p.ultimo_checkpoint < date() - duration('P7D')
WITH collect({nome:p.nome, ultimo:p.ultimo_checkpoint}) AS atrasados
RETURN atrasados;

// 4) Sugestões pendentes (Reflexão → Sugestão)
OPTIONAL MATCH (r:Reflexao)-[:SUGERIU]->(s:Sugestao)
RETURN s.descricao AS sugestao, s.prioridade AS prioridade
ORDER BY s.prioridade DESC;

// 5) Ajustes de parâmetros feitos pela camada reflexiva
OPTIONAL MATCH (r:Reflexao)-[:AJUSTOU]->(p:Parametro)
RETURN p.nome, p.valor_anterior, p.valor_novo, r.contexto, r.data
ORDER BY r.data DESC;

// 6) Saúde mínima do grafo (contagens)
RETURN
  size([(t:Tarefa) | 1])     AS tarefas,
  size([(p:Parametro) | 1])  AS parametros,
  size([(s:Sugestao) | 1])   AS sugestoes,
  size([(x:Reflexao) | 1])   AS reflexoes;
