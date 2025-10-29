// Catálogo operacional do Menir - Projetos Renderização e Textos

MERGE (render:Projeto {id: 'renderizacao'})
SET
  render.nome = 'Projeto Renderização',
  render.descricao = 'Pipeline SketchUp -> MyArchitect AI',
  render.status = 'em_andamento',
  render.atualizado = datetime()
WITH render
UNWIND [
  {id: 'renderizacao-capta-modelo', nome: 'Captura do modelo SketchUp', ordem: 1},
  {id: 'renderizacao-prepara-assets', nome: 'Preparar assets e referências', ordem: 2},
  {id: 'renderizacao-myarchitect', nome: 'Processar no MyArchitect AI', ordem: 3},
  {id: 'renderizacao-review', nome: 'Revisão e aprovação', ordem: 4}
] AS etapa
MERGE (e:Etapa {id: etapa.id})
SET
  e.nome = etapa.nome,
  e.ordem = etapa.ordem,
  e.atualizado = datetime()
MERGE (render)-[:TEM_ETAPA]->(e);

MERGE (textos:Projeto {id: 'textos'})
SET
  textos.nome = 'Projeto Textos',
  textos.descricao = 'Documentos e conversas operacionais do Menir',
  textos.status = 'ativo',
  textos.atualizado = datetime()
WITH textos
UNWIND [
  {id: 'texto-briefing-operacional', titulo: 'Briefing Operacional'},
  {id: 'texto-protocolo-ponte', titulo: 'Protocolo Ponte - Conversas'},
  {id: 'texto-gatomia-notas', titulo: 'Notas Gatomia'},
  {id: 'texto-filosomia', titulo: 'Filosomia - Diario'},
  {id: 'texto-amd', titulo: 'Relatos AMD'}
] AS doc
MERGE (d:Documento {id: doc.id})
SET
  d.titulo = doc.titulo,
  d.status = 'em_fluxo',
  d.atualizado = datetime()
MERGE (textos)-[:CONTEM]->(d);

MATCH (proj:Projeto)
OPTIONAL MATCH (proj)-[:TEM_ETAPA]->(etapa:Etapa)
OPTIONAL MATCH (proj)-[:CONTEM]->(doc:Documento)
RETURN
  proj.id AS projeto,
  proj.nome AS nome,
  proj.status AS status,
  collect(DISTINCT etapa.nome) AS etapas,
  collect(DISTINCT doc.titulo) AS documentos,
  proj.atualizado AS atualizado
ORDER BY projeto;
