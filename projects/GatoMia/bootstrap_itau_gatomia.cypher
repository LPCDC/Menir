////////////////////////////////////////////////////////////////////////
// Gatomia — Bootstrap do Projeto Itaú (Neo4j 5.x)
// Ações: ativar projeto, normalizar label, criar constraints/índices
// Notas: evitar acentos em labels; schema mínimo seguro para import
////////////////////////////////////////////////////////////////////////

/* 0) Parâmetros básicos */
:param NOW => datetime({timezone: 'America/Sao_Paulo'});

/* 1) Garantir nó do Projeto Itaú (ativo) */
MERGE (p:Projeto {slug:'Itau'})
  ON CREATE SET p.nome = 'Projeto Itaú',
                p.ativo = true,
                p.createdAt = $NOW
  ON MATCH  SET p.ativo = true,
                p.updatedAt = $NOW;

/* 2) Normalizar label: `Transação` -> Transacao (sem acento) */
CALL {
  MATCH (n:`Transação`)
  WITH n LIMIT 10000
  SET n:Transacao
  REMOVE n:`Transação`
  RETURN count(*) AS _moved
} IN TRANSACTIONS OF 10000 ROWS;

/* 3) Constraints/Índices — criar antes de imports */
CREATE CONSTRAINT IF NOT EXISTS projeto_slug_unique
FOR (p:Projeto) REQUIRE p.slug IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS pessoa_id_unique
FOR (x:Pessoa) REQUIRE x.id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS conta_id_unique
FOR (x:Conta) REQUIRE x.id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS documento_id_unique
FOR (x:Documento) REQUIRE x.id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS transacao_id_unique
FOR (x:Transacao) REQUIRE x.id IS UNIQUE;

/* (opcional, se usar chaves naturais) */
CREATE INDEX IF NOT EXISTS transacao_data_idx
FOR (x:Transacao) ON (x.data);

/* 4) Validação de tipos de relacionamento (propriedades mínimas) */
CREATE CONSTRAINT IF NOT EXISTS refere_a_uid_exists
FOR ()-[r:REFERE_A]-() REQUIRE r.uid IS NOT NULL;

CREATE CONSTRAINT IF NOT EXISTS envolvendo_uid_exists
FOR ()-[r:ENVOLVENDO]-() REQUIRE r.uid IS NOT NULL;

/* 5) Higiene opcional de tipos em minúsculas (descomente se necessário) */
/*
CALL {
  MATCH (a)-[r:`refere_a`]->(b)
  CALL {
    WITH a,b,r
    CREATE (a)-[r2:REFERE_A]->(b)
    SET r2 += r
    DELETE r
    RETURN 1
  }
  RETURN count(*) AS moved_refere
} IN TRANSACTIONS OF 10000 ROWS;

CALL {
  MATCH (a)-[r:`envolvendo`]->(b)
  CALL {
    WITH a,b,r
    CREATE (a)-[r2:ENVOLVENDO]->(b)
    SET r2 += r
    DELETE r
    RETURN 1
  }
  RETURN count(*) AS moved_env
} IN TRANSACTIONS OF 10000 ROWS;
*/

/* 6) Marcar checkpoint no projeto */
MATCH (p:Projeto {slug:'Itau'})
SET p.lastBootstrapAt = $NOW;
