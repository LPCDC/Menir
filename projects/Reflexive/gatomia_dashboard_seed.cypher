// ======================================
// Trigger oficial: Gato Mia
// ======================================
MERGE (t:Tarefa {id: "gatomia_trigger"})
ON CREATE SET t.nome = "Checkpoint Gato Mia",
              t.descricao = "Trigger alternativo/bilingue de Marco Polo",
              t.frase = "Miauuuuuu — eis o painel"
