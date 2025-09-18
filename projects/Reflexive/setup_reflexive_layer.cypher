// ======================================
// Menir Reflexive Layer — Setup
// ======================================

// Cria constraints básicos
CREATE CONSTRAINT reflexao_id IF NOT EXISTS
FOR (r:Reflexao) REQUIRE r.id IS UNIQUE;

CREATE CONSTRAINT tarefa_id IF NOT EXISTS
FOR (t:Tarefa) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT problema_desc IF NOT EXISTS
FOR (p:Problema) REQUIRE p.descricao IS UNIQUE;

CREATE CONSTRAINT solucao_desc IF NOT EXISTS
FOR (s:Solucao) REQUIRE s.descricao IS UNIQUE;

CREATE CONSTRAINT sugestao_desc IF NOT EXISTS
FOR (sg:Sugestao) REQUIRE sg.descricao IS UNIQUE;

CREATE CONSTRAINT parametro_nome IF NOT EXISTS
FOR (pa:Parametro) REQUIRE pa.nome IS UNIQUE;

CREATE CONSTRAINT rota_id IF NOT EXISTS
FOR (re:RotaEnergetica) REQUIRE re.id IS UNIQUE;

CREATE CONSTRAINT subgrafo_id IF NOT EXISTS
FOR (sgf:Subgrafo) REQUIRE sgf.id IS UNIQUE;

CREATE CONSTRAINT bloco_hash IF NOT EXISTS
FOR (b:BlocoAuditavel) REQUIRE b.hash IS UNIQUE;

CREATE CONSTRAINT prompt_id IF NOT EXISTS
FOR (pr:Prompt) REQUIRE pr.id IS UNIQUE;

// ======================================
// Exemplo de ingestão reflexiva
// ======================================

MERGE (t:Tarefa {id: "itau_csv_2025-09-19"})
MERGE (r:Reflexao {id: "ref_001"})
  ON CREATE SET r.data = datetime(),
                r.contexto = "Projeto Itaú ingestão CSV",
                r.duracao = 3200,
                r.tentativas = 3

MERGE (p:Problema {descricao: "Arquivo CSV não acessível", categoria: "acesso"})
MERGE (s:Solucao {descricao: "Publicar CSV via GitHub Pages", tipo: "workaround"})
MERGE (sg:Sugestao {descricao: "Automatizar criação de CSV com .bat", prioridade: "alta"})
MERGE (pa:Parametro {nome: "reasoning_effort"})
  ON CREATE SET pa.valor_anterior = "rápido", pa.valor_novo = "intermediário"

MERGE (ro:RotaEnergetica {id:"rota001"})
  ON CREATE SET ro.opcao = "Cypher local", ro.custo = "baixo"

MERGE (sb:Subgrafo {id:"exp001"})
  ON CREATE SET sb.descricao = "Explicação de vínculos Parte-Documento"

MERGE (bl:BlocoAuditavel {hash:"abc123"})
MERGE (pr:Prompt {id:"prompt001"})
  ON CREATE SET pr.original = "Resumo Itaú",
                pr.otimizado = "Resumo Itaú com foco em transações de alto valor"

MERGE (t)-[:GEROU]->(r)
MERGE (r)-[:IDENTIFICOU]->(p)
MERGE (r)-[:RESOLVEU_COM]->(s)
MERGE (r)-[:SUGERIU]->(sg)
MERGE (r)-[:AJUSTOU]->(pa)
MERGE (r)-[:AVALIOU]->(ro)
MERGE (r)-[:GEROU_EXPLICACAO]->(sb)
MERGE (r)-[:ASSINADO_EM]->(bl)
MERGE (r)-[:OTIMIZOU_PROMPT]->(pr);
