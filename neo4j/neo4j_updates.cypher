:param NOW => datetime({timezone: 'America/Sao_Paulo'});

// Constraints
CREATE CONSTRAINT eventobanco_id_unique IF NOT EXISTS FOR (e:EventoBanco) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT transacao_id_unique  IF NOT EXISTS FOR (t:Transacao)  REQUIRE t.id IS UNIQUE;

// Projeto e Conta
MERGE (p:Projeto {slug: 'Itau'})
  ON CREATE SET p.nome = 'Projeto Itaú', p.ativo = true, p.createdAt = $NOW
  ON MATCH  SET p.ativo = true, p.updatedAt = $NOW;

MERGE (c:Conta {id: '15220012'})
  ON CREATE SET c.createdAt = $NOW
  ON MATCH  SET c.updatedAt = $NOW;

// EventoBanco
MERGE (e:EventoBanco {id: 'REG-2025-10-001'})
SET
  e.atendente     = 'Silva',
  e.data          = date('2025-09-29'),
  e.conta         = '15220012',
  e.status        = 'negativa em 2025-10-10',
  e.pedido        = 'vídeo agência',
  e.fonte         = 'interação humana',
  e.lastStatusDate= date('2025-10-10'),
  e.createdAt     = coalesce(e.createdAt, $NOW),
  e.updatedAt     = $NOW;

// Relações
MERGE (e)-[:REFERE_A   {uid: 'REG-2025-10-001#Itau'}]->(p);
MERGE (e)-[:ENVOLVENDO {uid: 'REG-2025-10-001#15220012'}]->(c);

RETURN e, p, c;

// requires_push_agent: true
