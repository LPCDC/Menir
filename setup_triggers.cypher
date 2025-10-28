// ================================
// MENIR — Setup Triggers (Marco, Eco, Gato Mia)
// ================================

// Marco
MERGE (m:Trigger {nome:"Marco"})
ON CREATE SET m.resposta = "civil da internet",
              m.ativo = true,
              m.data_registro = datetime()
ON MATCH SET m.ativo = true;

// Eco
MERGE (e:Trigger {nome:"Eco"})
ON CREATE SET e.resposta = "ECO é a resposta da charada do teste de persistência",
              e.ativo = true,
              e.data_registro = datetime()
ON MATCH SET e.ativo = true;

// Gato Mia
MERGE (g:Trigger {nome:"Gato Mia"})
ON CREATE SET g.resposta = "Miau! 🐾 Dashboard completo do Menir carregado.",
              g.ativo = true,
              g.data_registro = datetime()
ON MATCH SET g.ativo = true;
