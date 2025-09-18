// ==========================================================
// Itaú Queries Pack - Judicial Analysis
// ==========================================================

// Contar contas
MATCH (c:Conta) RETURN count(c) AS contas;

// Contar transações
MATCH (t:Transacao) RETURN count(t) AS transacoes;

// Saldo diário (exemplo para conta 123)
MATCH (c:Conta {id:"123"})-[:REGISTRA]->(t:Transacao)
RETURN t.data AS dia, sum(t.valor) AS saldo_dia
ORDER BY dia;

// Linha do tempo completa
MATCH (c:Conta {id:"123"})-[:REGISTRA]->(t:Transacao)
OPTIONAL MATCH (t)<-[:RELACIONADO_A]-(d:Documento)
OPTIONAL MATCH (c)<-[:ENVOLVIDO]-(p:Parte)
RETURN t.data, t.tipo, t.valor, t.descricao, d.nome AS documento, p.nome AS parte
ORDER BY t.data;

// Transações suspeitas (valor > 1000)
MATCH (c:Conta)-[:REGISTRA]->(t:Transacao)
WHERE abs(t.valor) > 1000
RETURN c.id, t.data, t.valor, t.descricao
ORDER BY t.valor DESC;
