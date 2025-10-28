// ==========================================================
// itaui.js - Ingestão Itaú no Neo4j Aura
// ==========================================================
// Requer: Node.js + pacote neo4j-driver
// Instale: npm install neo4j-driver
// ==========================================================

import neo4j from 'neo4j-driver';

const uri = process.env.NEO4J_URI || "neo4j+s://<seu-endpoint>.databases.neo4j.io";
const user = process.env.NEO4J_USER || "neo4j";
const password = process.env.NEO4J_PASSWORD || "<sua-senha>";

const driver = neo4j.driver(uri, neo4j.auth.basic(user, password));

async function main() {
  const session = driver.session();

  try {
    // Constraints
    await session.run(`CREATE CONSTRAINT itau_conta_id IF NOT EXISTS FOR (c:Conta) REQUIRE c.id IS UNIQUE`);
    await session.run(`CREATE CONSTRAINT itau_transacao_id IF NOT EXISTS FOR (t:Transacao) REQUIRE t.id IS UNIQUE`);
    await session.run(`CREATE CONSTRAINT itau_doc_id IF NOT EXISTS FOR (d:Documento) REQUIRE d.id IS UNIQUE`);
    await session.run(`CREATE CONSTRAINT itau_parte_id IF NOT EXISTS FOR (p:Parte) REQUIRE p.id IS UNIQUE`);
    console.log("✅ Constraints criadas.");

    // Exemplo de ingestão
    await session.run(`
      MERGE (c:Conta {id: "123"})
        ON CREATE SET c.agencia = "0001", c.numero = "98765"
      MERGE (t:Transacao {id: "tx001"})
        ON CREATE SET t.data = date("2025-09-18"), t.valor = 500.0, t.tipo = "debito", t.descricao = "Teste inicial"
      MERGE (c)-[:REGISTRA]->(t)
    `);
    console.log("✅ Conta + Transação exemplo inseridas.");
  } catch (err) {
    console.error("❌ Erro:", err);
  } finally {
    await session.close();
    await driver.close();
  }
}

main();
