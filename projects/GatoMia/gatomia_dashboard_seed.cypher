// ======================================
// Menir — Seeds para MarcoPolo + GatoMia + Gatuninha
// ======================================

// Card 1 — Projetos ativos (compacto)
OPTIONAL MATCH (prj:Projeto)
WITH COLLECT(coalesce(prj.nome,'(sem nome)'))[0..10] AS projs
RETURN "MarcoPolo/GatoMia/Gatuninha" AS gatilho,
       apoc.text.join(projs, ', ') AS projetos_ativos
LIMIT 1;

// Card 2 — Problemas recentes (top 5)
OPTIONAL MATCH (r:Reflexao)-[:IDENTIFICOU]->(p:Problema)
WITH r,p ORDER BY r.data DESC
RETURN "MarcoPolo/GatoMia/Gatuninha" AS gatilho,
       p.categoria AS categoria,
       p.descricao AS problema,
       r.contexto AS contexto,
       toString(r.data) AS quando
LIMIT 5;

// Card 3 — Sugestões pendentes (top 5)
OPTIONAL MATCH (r:Reflexao)-[:SUGERIU]->(s:Sugestao)
WITH r,s ORDER BY r.data DESC
RETURN "MarcoPolo/GatoMia/Gatuninha" AS gatilho,
       s.prioridade AS prioridade,
       s.descricao AS sugestao,
       r.contexto AS origem
LIMIT 5;

// Card 4 — Ajustes de parâmetros (recentes)
OPTIONAL MATCH (r:Reflexao)-[:AJUSTOU]->(pa:Parametro)
WITH r,pa ORDER BY r.data DESC
RETURN "MarcoPolo/GatoMia/Gatuninha" AS gatilho,
       pa.nome AS parametro,
       pa.valor_anterior AS de,
       pa.valor_novo AS para,
       toString(r.data) AS quando
LIMIT 10;
