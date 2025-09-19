////////////////////////////////////////////////////////////////////////
// normalize_transacao_label.cypher
// Normaliza label “Transação” para “Transacao”
////////////////////////////////////////////////////////////////////////

// Diagnóstico: ver se há nós com label acentuado
MATCH (n)
WHERE labels(n) CONTAINS "Transação"
RETURN DISTINCT labels(n) AS labels, count(n) AS quantidade;

// Diagnóstico: ver se há nós já com o label sem acento
MATCH (n)
WHERE labels(n) CONTAINS "Transacao"
RETURN DISTINCT labels(n) AS labels, count(n) AS quantidade;

// Padronização: renomear label acentuado para versão sem acento
CALL {
  MATCH (n:`Transação`)
  REMOVE n:`Transação`
  SET n:Transacao
  RETURN count(n) AS converted
}
RETURN converted;
