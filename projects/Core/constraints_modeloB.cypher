// constraints_modeloB.cypher
// Versão correta das constraints de unicidade para Modelo B

CREATE CONSTRAINT empresa_id_unique IF NOT EXISTS
FOR (e:Empresa) REQUIRE e.id IS UNIQUE;

CREATE CONSTRAINT projeto_id_unique IF NOT EXISTS
FOR (p:Projeto) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT cliente_id_unique IF NOT EXISTS
FOR (c:Cliente) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT pessoa_id_unique IF NOT EXISTS
FOR (pers:Pessoa) REQUIRE pers.id IS UNIQUE;

CREATE CONSTRAINT servico_id_unique IF NOT EXISTS
FOR (s:Servico) REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT engajamento_id_unique IF NOT EXISTS
FOR (eng:Engajamento) REQUIRE eng.id IS UNIQUE;

CREATE CONSTRAINT prompttemplate_id_unique IF NOT EXISTS
FOR (t:PromptTemplate) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT menu_nome_unique IF NOT EXISTS
FOR (menu:Menu) REQUIRE menu.nome IS UNIQUE;
