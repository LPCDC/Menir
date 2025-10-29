CREATE CONSTRAINT sistema_id IF NOT EXISTS FOR (s:Sistema) REQUIRE s.id IS UNIQUE;

WITH [
  {id: 'anti-placebo-v1-1', nome: 'Anti-Placebo v1.1', cluster: 'OPERAR', status: 'ativo'},
  {id: 'dash-cloak-v3-5', nome: 'Dash Cloak v3.5', cluster: 'OPERAR', status: 'ativo'},
  {id: 'gatomia-bootstrap', nome: 'Gatomia Bootstrap', cluster: 'ATUAR', status: 'ativo'},
  {id: 'slowdown-guard-v0-3', nome: 'Slowdown Guard v0.3', cluster: 'PRESERVAR', status: 'ativo'},
  {id: 'memory-check-v2', nome: 'Memory Check v2', cluster: 'PRESERVAR', status: 'ativo'},
  {id: 'prompt-master', nome: 'Prompt Master', cluster: 'GERAR', status: 'ativo'},
  {id: 'qa-2-pass', nome: 'QA 2-pass', cluster: 'GERAR', status: 'ativo'},
  {id: 'friend-box', nome: 'Friend Box', cluster: 'ATUAR', status: 'ativo'},
  {id: 'protocolo-ponte', nome: 'Protocolo Ponte', cluster: 'OPERAR', status: 'ativo'},
  {id: 'filosomia', nome: 'Filosomia', cluster: 'ATUAR', status: 'ativo'}
] AS sistemas
UNWIND sistemas AS sistema
MERGE (s:Sistema {id: sistema.id})
SET
  s.nome = sistema.nome,
  s.cluster = sistema.cluster,
  s.status = sistema.status,
  s.atualizado = datetime()
WITH s, sistema
MERGE (c:Cluster {nome: sistema.cluster})
MERGE (s)-[:ATIVO_EM]->(c);

MATCH (s:Sistema)-[:ATIVO_EM]->(c:Cluster)
RETURN c.nome AS cluster, s.nome AS sistema, s.status AS status, s.atualizado AS atualizado
ORDER BY cluster, sistema;
