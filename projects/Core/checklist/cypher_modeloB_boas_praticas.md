MENIR-CHECKLIST: Boas práticas de Cypher e modelo de Engajamento

1. ALWAYS usar WITH entre SET/MERGE e UNWIND quando variáveis definidas (MERGE/SET) forem usadas depois em UNWIND ou em blocos subsequentes.  
2. Criar nó Engajamento/Contrato quando  
    a) for necessário armazenar escopo, status, datas, valores;  
    b) houver cliente + empresa + projeto + múltiplos serviços;  
    c) quiser histórico ou capacidade de auditoria/faturamento.  
3. Nomes de IDs devem ser padronizados: minúsculos, underscores, sem acentos. Ex: “tovolli”, “familia_otani”, “serv_renderizacao”.  
4. Separar empresa/profissional/cliente claramente:  
    - Empresa: LibLabs, Hexágono etc.  
    - Pessoa: profissional (Tânia Mara, Carol etc.)  
    - Cliente: destinatário do serviço.  
5. Prompt Improver como sistema fixo: registrar melhorias de prompt como eventos vinculados a Engajamento ou Projeto.  
6. PromptTemplate ligado a Projeto para reutilização, com exemplos claros (ambientação, horário, estilo).  
7. Menu / Branding visível: sistemas fixos (como Prompt Improver) devem aparecer no menu principal (OPERAR) ou outro cluster visível.  
8. Evitar super-fragmentação: agrupar entidades quando possível, para não poluir grafo nem lentidão.  
9. Todos erros sintáticos (ex: “missing WITH”) devem ser registrados como eventos de erro no grafo (ex: nó Evento {tipo:"erro_cypher", mensagem, contexto, hora}) para aprendizado automático.  
10. Confirmar resultados de scripts → rodar no ambiente de teste/dry-run antes de commit “produção”.

---
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

Mantenha esse documento versionado dentro de:  
`projects/Core/checklists/cypher_modeloB_boas_praticas.md`
