// Órfãos
MATCH (d:Documento) WHERE NOT (d)-[:REFERE_A]->(:Projeto) RETURN d.id AS doc_orfao LIMIT 200;

// Threads quebradas (email com In-Reply-To mas sem REPLY_TO)
MATCH (m:Documento {doc_type:'email'}) WHERE m.in_reply_to IS NOT NULL AND NOT (m)-[:REPLY_TO]->() RETURN m.id AS email_sem_thread LIMIT 200;

// Contas sem transações 90 dias
MATCH (c:Conta) WHERE NOT (c)<-[:ENVOLVENDO]-(:Transacao) RETURN c.id AS conta_sem_tx;

// Duplicados exatos (sha256)
MATCH (a:Documento),(b:Documento) WHERE a.sha256 = b.sha256 AND a.id < b.id RETURN a.id AS dup_a, b.id AS dup_b LIMIT 200;
