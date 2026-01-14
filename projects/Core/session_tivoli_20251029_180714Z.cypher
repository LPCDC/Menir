MERGE (p:Projeto {id:'tivoli'})
SET
  p.nome = 'tivoli',
  p.ultimo_update = datetime('2025-10-29T18:07:14Z'),
  p.resumo = @'Bia não conseguiu mexer ontem por motivo pessoal. Hoje confirmou que já tem calçada/poste/árvore medidos no sketch antigo mas esqueceu de redesenhar. Falta medir alturas reais dos muros e muretas para fechar sombra e leitura do pé-direito. Carol quer o sketch pronto 2025-10-30.',
  p.bloqueios = @'Precisamos medir altura do muro de trás (divisa prédio vizinho), da mureta lateral da garagem e da divisória entre as duas garagens de serviço. Sem essas medidas o sketch não fecha. Bia só consegue mexer em casa porque na prefeitura não tem SketchUp.',
  p.prazo_sketch = date('2025-10-30'),
  p.prazo_cad = date('2025-11-03'),
  p.participantes = 'Bia (sketch/CAD), Carol (coordena prazo e cliente), Luiz Paulo (continuidade execução), clientes (reunião semana que vem)';
