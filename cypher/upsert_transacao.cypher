MERGE (c:Conta {id:$conta})
MERGE (t:Transacao {id:$txid})
  ON CREATE SET t.data=date($data), t.valor=toFloat($valor), t.moeda=$moeda, t.ref_banco=$ref, t.descricao=$descricao
MERGE (t)-[:ENVOLVENDO]->(c);
