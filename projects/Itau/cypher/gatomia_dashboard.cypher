/* gatomia_dashboard.cypher */
MATCH (t:Transacao) RETURN count(t) AS transacoes;
MATCH (c:Conta) RETURN count(c) AS contas;
MATCH (p:Pessoa) RETURN count(p) AS pessoas;
MATCH (d:Documento) RETURN count(d) AS documentos;
MATCH (:Transacao)-[:REFERE_A]->(:Documento) RETURN count(*) AS rels_refere_a;
MATCH (:Transacao)-[:ENVOLVENDO]->(:Pessoa) RETURN count(*) AS rels_envolvendo;
