// ==========================================================
// Itaú Ingest - Menir Judicial Dataset
// ==========================================================

// Constraints
CREATE CONSTRAINT itau_conta_id IF NOT EXISTS
FOR (c:Conta) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT itau_transacao_id IF NOT EXISTS
FOR (t:Transacao) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT itau_doc_id IF NOT EXISTS
FOR (d:Documento) REQUIRE d.id IS UNIQUE;

CREATE CONSTRAINT itau_parte_id IF NOT EXISTS
FOR (p:Parte) REQUIRE p.id IS UNIQUE;

// Exemplo de ingestão simples
MERGE (c:Conta {id: "123"})
  ON CREATE SET c.agencia = "0001", c.numero = "98765"
MERGE (t:Transacao {id: "tx001"})
  ON CREATE SET t.data = date("2025-09-18"), t.valor = 500.0, t.tipo = "debito", t.descricao = "Teste inicial"
MERGE (c)-[:REGISTRA]->(t);
