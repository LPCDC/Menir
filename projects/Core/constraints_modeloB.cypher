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

CREATE CONSTRAINT promptTemplate_id_unique IF NOT EXISTS
FOR (pt:PromptTemplate) REQUIRE pt.id IS UNIQUE;

CREATE CONSTRAINT menu_nome_unique IF NOT EXISTS
FOR (m:Menu) REQUIRE m.nome IS UNIQUE;
