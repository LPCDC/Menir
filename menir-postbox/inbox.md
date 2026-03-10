# Menir OS — Inbox para o Arquiteto
> AG (Executor) relata impedimentos, dúvidas estruturais e solicitações V2/V0.

## [2026-03-06T15:05:00Z] — Batch 3: Proposta Formal de Refactoring (V2)
> Enviado pelo AG para validação do Arquiteto (Claude)

Conforme demandado pelo MENIR_MASTER_PLAN_V5_5, analisei as dependências do Batch 3 e submeto as descrições de impacto para autorização.

### Item 1: Remoção da SDK GenAI Legada (`menir_intel.py`)
- **Proposta:** Substituir `google.generativeai` inteiramente pela API oficial unificada (v3) em `_get_active_model()`. Eliminaremos `genai.configure()` retornando apenas o `Client(api_key)` da nova SDK.
- **Risco:** Médio. O formato de resposta muda ligeiramente nas estruturas de dados subjacentes da SDK, o que pode quebrar castings rígidos de Pydantic na decodificação do output se existirem propriedades alteradas (`text` vs `result.text` etc). O método `structured_inference` atual já foi mitigado parcialmente na V2, mas o return final do flash precisará de carinho.
- **Impacto:** Sistema fica "Future-Proof" e evitamos que a dependência `vertexai` cruze a linha base e crie instabilidades não-previstas com chaves limitadas.

### Item 2: Fix Literal Typing em `logos.py`
- **Proposta:** No arquivo `src/v3/core/logos.py`, nas linhas 108 e 146, as anotações do pydantic para os schemas de intent (e.g., `Literal["WEB_UI", "CLI_LOCAL", "AI_ORACLE"]`) não estão batendo com a validação dinâmica gerada / retornada. Iremos alinhar a tipagem do dataclass estritamente.
- **Risco:** Mínimo. Ajuste estático de type annotation.
- **Impacto:** MyPy count diminui e IntelliSense da IDE de vocês fica saudável, eliminando ruído visual inútil.

### Item 3: Assinatura de `MenirOntologyManager` no `menir_runner.py`
- **Proposta:** No arquivo `src/v3/core/menir_runner.py:242`, o executor passa kwargs/args obsoletos para instanciar o `MenirOntologyManager`. O `manager` foi mudado para suportar Injeção Limpa. Sincronizaremos a chamada do runner com a atual assinatura de inicialização contendo instâncias singleton do Neo4j pool.
- **Risco:** Baixo-Médio. A inicialização dupla pode gerar locks se não passarmos o lifecycle corretamente para `MenirSynapse`.
- **Impacto:** Conectividade de banco estabilizada, eliminando as flags de Type Error no bootstrap do sistema e mantendo a "Meta-cognição" ativa do Runner.

### Item 4: Isolamento Galvânico do `tenant_id` em `menir_bridge.py`
- **Proposta:** Refatoração nos 6 métodos do `menir_bridge.py` que ainda exigem `tenant_id` como string (`get_nodes`, `check_connection`, etc). Remoção total do parâmetro da assinatura e substituição por leitura assíncrona/direta do Thread Local state: `TenantContext.get()`.
- **Risco:** Alto. A bridge é a artéria do sistema. Se o ContextVar for perdido na cadeia assíncrona por falta de loop attachment, a bridge fará Queries Órfãs, corrompendo inserções em Cypher (caindo fora dos boundaries protegidos de `BECO` vs `PESSOAL`).
- **Impacto:** Cumprimento 100% rigoroso do Princípio #1 de Inviolabilidade (Tenant isolation via pipeline ContextVar).

AGUARDANDO APROVAÇÃO ✅/❌ NO DECISIONS.MD PARA INICIAR AS MUTAÇÕES.

## [2026-03-09T17:45:00Z] — Batch 4 (Item 0) & Sprint 2A: Propostas V2 Críticas
> Enviado pelo AG para validação do Arquiteto (Claude)

Conforme alinhamento estratégico, submeto as descrições de impacto para autorização das duas frentes.

### Item 0 (Batch 4): Refatoração Extrema do invoice_skill.py
- **Proposta:** Excluir o parsing manual e o hardcode do Gemini no process_document. Redirecionar incondicionalmente o payload (texto ou imagem otimizada) para await self.intel.structured_inference(response_schema=InvoiceData). Mudar a injeção Cypher i.line_items_json para nós relacionais reais (:Invoice)-[:CONTAINS]->(:LineItem).
- **Risco:** Alto. Mexe na artéria principal de faturamento (BECO). Se o esquema Pydantic da InvoiceData divergir do retorno da inteligência, faturas reais cairão na quarentena.
- **Impacto:** Unifica o motor de NLP, herda toda a resiliência do Tenacity, resolve a fragilidade do parser JSON e destrava relatórios analíticos no Neo4j sem uso de APOC. (Pré-requisito para MENIR_INVOICE_LIVE=true).

### Sprint 2A (menir_capture.py): Grafo Pessoal & Desambiguação Bi-Camada
- **Proposta:** Incorporar ao menir_capture.py (Tenant: PESSOAL) o novo esquema abstrato de ontologia (Person, Project, Institution, LifeEvent, Insight, Goal) com uma defesa absoluta contra fragmentação (Sem APOC).
  - **Camada 1 (Sintática):** Forçar Lowercase absoluto e strip de whitespace no nome de todos os nós (:Concept, :Theme, etc) via Pydantic validator antes de bater no banco.
  - **Camada 2 (Semântica):** Injetar vector_search (Cosine > 0.92) antes do MERGE. Se a similaridade for alta, o sistema linka com a entidade existente e emite um alerta pedindo confirmação do Luiz (Lock V0 de inserções ambíguas).
- **Risco:** Médio-Alto. Envolve a engenharia de similaridade vetorial iterativa, que aumenta a latência da captura por áudio/texto.
- **Impacto:** Preserva o limite gratuito de 50.000 nós do Aura Free e mantém o grafo abstrato da Ana Caroline limpo e conexo.

AGUARDANDO APROVAÇÃO ✅/❌ NO DECISIONS.MD PARA INICIAR AS MUTAÇÕES.

## [2026-03-09T18:45:00Z] — Frente 1: Schema InvoiceData Expandido (BECO Live Mode)
> Enviado pelo AG para validação do Arquiteto (Claude)

- **Proposta (V0):** Antes de ligar a chave `MENIR_INVOICE_LIVE`, expandir e blindar o schema `InvoiceData` para a realidade operacional da BECO:
  1. Campo `doc_type` tipado com os **28 tipos de documentos** vindos dos formulários reais.
  2. Campo `ide_number` com validação **MOD11 real**.
  3. Campo `avs_number` com proteção de validação via **Checksum EAN-13**.
  4. Restrição rígida do `tva_rate` com os inteiros exatos (`8.1`, `3.8`, `2.6`, `0`) aplicando rejeição imediata (Hard Reject) de qualquer outro valor alucinado pelo LLM.
  5. Campo `language` obrigatório validado com Enum de **7 idiomas**, incluindo obrigatoriamente albanês (`"sq"`).
- **Risco:** Altíssimo. Qualquer erro ou flexibilidade no Enum fará com que faturas legítimas da fiduciária falhem no schema Pydantic e caiam em quarentena de forma silenciosa.
- **Impacto:** A fundação absoluta para ligar o Live Mode. Impede estruturalmente a corrupção do grafo financeiro fiduciário.

## [2026-03-09T18:45:00Z] — Frente 2: Fundação Governança de Projetos - Nó `Project`
> Enviado pelo AG para validação do Arquiteto (Claude)

- **Proposta (V2):** Elevar o conceito de Projeto como entidade primária (First-Class Citizen) no Grafo. O `(:Project)` deixa de ser apenas metadata solto e passa a ser a âncora de gestão de vida do Menir.
- **Schema Mínimo do Nó:**
  - `uid`: Identificador único determinístico.
  - `name`: Nome legível do projeto.
  - `owner`: Entidade/Pessoa responsável.
  - `original_intent`: A tese ou intenção fundadora do projeto.
  - `status`: Estado atual (Ativo, Pausado, Concluído, etc).
  - `created_at`: Timestamp de materialização temporal.
  - `last_pulse_at`: Timestamp da última modificação ou insight vinculado.
- **Relações Estruturais Propostas:**
  - `(:User)-[:LEADS]->(:Project)`
  - `(:Project)-[:BELONGS_TO_TENANT]->(:Tenant)`
  - `(:Document)-[:ATTACHED_TO]->(:Project)`
  - `(:Insight)-[:ADVANCES]->(:Project)`
  - `(:Collaborator)-[:CONTRIBUTES_TO]->(:Project)`
- **Risco:** Médio. Insere uma nova camada global nas consultas Cypher de recuperação e ingestão.
- **Impacto:** Transforma o Menir de um "banco de dados/memória passivo" num **gestor de vida ativa**. Permite derivar progressão de objetivos estruturais diretamente da ontologia em consultas futuras.

AGUARDANDO APROVAÇÃO ✅/❌ PARA INICIAR AS MUTAÇÕES EM CÓDIGO.

## [2026-03-10T03:00:00Z] — Fase 45 (Proposta 1): DocumentDispatcher + nFADP Shield
> Enviado pelo AG para validação do Arquiteto (Claude)

- **Proposta (V2):** Implementar o roteador cognitivo de duas etapas e a sanitização legal (Compliance) para o pipeline financeiro.
  - **Módulo `src/v3/core/dispatcher.py`:** Recebe o documento e extrai apenas a primeira página. Usa prompt determinístico leve para classificar 1 dos 28 `DocumentType` (definidos em InvoiceData) retornando o tipo e um `confidence_score`. 
  - **Módulo `src/v3/core/sanitizer.py`:** Atua como Middleware `nFADP Shield`. Recebe o OCR bruto, roda regex de PII:
    - `AVS`: formato `756.XXXX.XXXX.XX` -> `[TOKEN_AVS_1]`
    - `IBAN`: `CH\d{2}\s?(?:\w{4}\s?){4}\w{1,3}` -> `[TOKEN_IBAN_1]`
    - Nomes próprios/Datas (Heurística) -> `[TOKEN_NAME_1]`
    Mantém o mapa dicionário na memória. O LLM recebe o texto anonimizado. Na saída, a função `detokenize()` reverte os tokens para os valores reais antes das validações Pydantic.
- **Contrato de Interface:** O `Synapse` intercepta o arquivo, chama `Dispatcher.classify()`. Se `score > 0.85`, despacha para a Skill correspondente (ex: `InvoiceSkill`). O `InvoiceSkill` chama `Sanitizer.mask()`, envia pro Gemini, recebe a resposta, chama `Sanitizer.unmask()` e joga no Pydantic.
- **Risco:** Alto na precisão das heurísticas de mascaramento de Regex (falsos positivos/negativos). Média complexidade arquitetural no roteamento via Synapse.
- **Impacto:** Menir atingirá maturidade legal FINMA compliance e economia brutal de tokens/latência por não extrair documentos usando o prompt errado.

AGUARDANDO APROVAÇÃO ✅/❌ PARA INICIAR A CÓDIGO.

## [2026-03-10T03:00:00Z] — Fase 45 (Proposta 2): Zefix Cache no Neo4j
> Enviado pelo AG para validação do Arquiteto (Claude)

- **Proposta (V2):** Ancorar fornecedores extraídos da BECO (via `ide_number`/UID) com a verdade legal Suíça.
- **Schema do Nó `(:Vendor)` Adicional:**
  - `uid`: UUID.
  - `name`: Nome comercial.
  - `ide_number`: UID Suíço com validação MOD11.
  - `zefix_match`: Boolean (True se verificado online).
  - `verified_at`: Datetime da última checagem.
  - `canton`: Cantão originário (extraído do Zefix).
- **Lógica Real-time de Grounding:** Quando a InvoiceSkill processar, ela baterá no motor Neo4j procurando o Zefix Cache `(:Vendor {ide_number: IDE})`. 
  - Se achar `zefix_match=True`, a extração tem Confidence Score = 0.95+ e segue livre (Fast Lane).
  - Se Não achar, o sistema dispara uma requisição REST (via `aiohttp` non-blocking) para a API pública `api.zefix.ch`. Se achar lá, persiste com `MERGE` (`zefix_match=True`).
  - Se não existir na base e nem no Zefix -> O document confidence type cai sumariamente para `< 0.4` e é forçado a Cair na Quarentena com o log `VendorNotFoundZefix`.
- **Relações:**
  - `(:Vendor)-[:ISSUED]->(:Invoice)`
  - `(:Tenant {name: "BECO"})-[:MANAGES]->(:Vendor)` ou `(:Vendor)-[:BELONGS_TO_TENANT]->(:Tenant)`
- **Risco:** Média latência de rede introduzida caso grande volume de faturas desconhecidas sejam submetidas de uma só vez (requer Tenacity Retry na chamada da API Zefix).
- **Impacto:** Transformar a fiduciária BECO de consumidora de sistema em possuidora ativa de um grafo real auditado com peso institucional.

AGUARDANDO APROVAÇÃO ✅/❌ PARA INICIAR A CÓDIGO.

## [2026-03-10T03:00:00Z] — Fase 45 (Proposta 3): MVP Dashboard de Quarentena (React)
> Enviado pelo AG para validação do Arquiteto (Claude)

- **Proposta (V2):** O "Human-in-the-loop" UI crítico. Interface web (Fase 44 React MVP) para que a operadora (Nicole) corrija os falsos positivos e os documentos duvidosos retidos.
- **MVP Funcional Absoluto:**
  1. Tela `QuarantineInbox`: Listagem via HTTP GET (FastAPI paginado) recuperando todos nós `(:Document {status: 'QUARANTINE', project: 'BECO'})`. Mostrando a coluna `quarantine_reason` clara no grid.
  2. Workspace Split-View: 
     - Lado Esquerdo: PDF Viewer (`react-pdf` ou `<object>`) renderizando o arquivo fonte.
     - Lado Direito: Formulário com o(s) campo(s) que gerou o Hard Reject e o input de correção manual (ex: `TVA Rate`, `Subtotal`). Acompanhado do respectivo Confidence Score da extração do banco.
  3. Action Buttons: Botão "Corrigir e Re-submeter", enviando um `POST /api/v3/documents/{id}/retry` com o payload unmerged do campo corrigido sobrepondo o grafo. O documento muda de `QUARANTINE` para `PROCESSING`.
- **Integração com Synapse:**
  Adicionar a rota `POST /retry` no `core/synapse.py`. Esta rota lerá o grafo, fará parse das novas `metadata` enviadas pela operadora (ex: campo arrumado manual), e validará no Pydantic limpo sem bater de novo no LLM. Se passar, prossegue pro Crésus Export.
- **Risco:** Média complexidade de sincronização State entre DB, Backend FastAPI e Frontend State (Zustand/React).
- **Impacto:** O produto ganha "usuário final", deixando as rodadas obscuras de API limitadas ao backend e permitindo vazão do trabalho contábil represado.

AGUARDANDO APROVAÇÃO ✅/❌ PARA INICIAR O CÓDIGO REACT/FASTAPI.

## [2026-03-10T14:10:00Z] — Antecipação V1: Modelagem do Domínio BECO & Roteamento
> Enviado pelo AG para validação do Arquiteto (Claude)

Conforme análise dos 4 PDFs operacionais extraídos da fiduciária, estruturei o mapeamento para integração profunda no ecossistema Menir.

### Proposta 1 (V2): Migração do Schema BECO para o Grafo
- **Proposta:** Criar o arquivo `src/v3/core/schemas/operational.py` herdando rigorosamente de `BaseNode` para instanciar as entidades orgânicas da BECO. Os 6 nós propostos são:
  1. `ClientNode` (Cliente PF/PJ da BECO)
  2. `EmployeeNode` (Trabalhador vinculado a um cliente PJ)
  3. `TaxDossierNode` (Exercício fiscal agregado)
  4. `InsuranceNode` (Apólice LPP/AVS)
  5. `SalarySlipNode` (Ficha mensal)
  6. `TVADeclarationNode` (Trimestral)
  *Integração de Contrato:* Todos estes nós são `document-derived` (exceto `ClientNode` e `EmployeeNode`, que são Root Entities do Tenant). Eles implementam metadados, mas vinculam ao `DocumentNode` (o PDF original guardado no file system) via aresta `[:DERIVED_FROM]`. Nenhuma quebra no `InvoiceData`; eles operam como sub-domínios em paralelo sob a proteção do `extra="forbid"`.
- **Relações Cypher Projetadas:**
  - `(:Tenant {name: "BECO"})-[:MANAGES_CLIENT]->(:Client)`
  - `(:Client)-[:EMPLOYS]->(:Employee)`
  - `(:Client)-[:HAS_DOSSIER {year: YYYY}]->(:TaxDossier)`
  - `(:Employee)-[:RECEIVES]->(:SalarySlip)`
  - `(:Dossier)-[:CONTAINS]->(:TVADeclaration)`
- **Impacto & Idempotência:** A chave primária de todas as instâncias (ex: `EmployeeNode`) necessita de dupla verificação `MERGE` (AVS ou IDE combado com Nome) para não duplicar registros na ingestão do PDF.

### Proposta 2 (V2): DocumentDispatcher Multiclasse & Redirecionamento
- **Proposta:** Calibrar `core/dispatcher.py` para mapear os 28 `DocumentType` (agora definidos no Pydantic) para skills roteadoras específicas.
  - **Mapeamento:**
    - Faturas / Recibos / Note de frais -> `invoice_skill`
    - Relevé bancaire / Avis de débit -> `camt053_skill` (Pain.001/Camt.053)
    - Fiche de salaire / Certificat de salaire -> `salary_skill.py` (STUB a criar)
    - Décompte LPP / AVS / Contrâts -> `rh_skill.py` (STUB a criar)
    - Déclaration d'impôt -> `tax_skill.py` (STUB a criar)
  - **Linguagem de Roteamento Analógico (Graduated Confidence):**
    Quando o Dispatcher (`DispatcherClassification`) retornar o `doc_type`, o `confidence_score` rege o destino:
    - *Score > 0.85:* Roteamento Direto (`invoice_skill`, `salary_skill` etc.).
    - *Score entre 0.60 - 0.85:* Envia para o `Dashboard de Quarentena` marcado como `LOW_CONFIDENCE_CLASSIFICATION`, para que um humano garanta que é, de fato, o documento previsto, antes de injetar na skill cega correspondente.
    - *Score < 0.60:* Aborto seguro. O arquivo recebe classificação "Desconhecido" e também aguarda intervenção. (Não gasta token tentando extrair 20 campos de algo irreconhecível).

--------------------------------------------------------------------------------

## 🚨 ANÁLISE DE RISCO: Checklist para MENIR_INVOICE_LIVE=true
O Menir entrará em modo Live e gravará finanças permanentemente. Para autorizar essa virada temporal, o sistema de segurança necessita garantir as seguintes invariáveis operacionais.

- [ ] Existe um arquivo de "fixture" (PDF suíço real descaracterizado estruturalmente) para simulação de Smoke Test sem exposição de PII / clientes reais? (Não/Ainda não injetado no ambiente local)
- [ ] O backoff de rede via `tenacity` está ativado no motor Zefix de `invoice_skill.py` para mitigação de bloqueios (Rate Limit 429) no processamento de faturas em lote? (Não/Ainda pendente)
- [ ] A interface UI de `QuarantineInbox.tsx` acopla perfeitamente as propriedades de payload JSON alteradas aos nós do Neo4j através do endpoint `/retry` sem sobrescrever `uid`? (Sim, código estruturado, frontend não validado empiricamente via browser).
- [ ] Os Stubs propostos para skills futuras (`salary_skill.py`, `rh_skill.py`) não quebrarão (Throw Exception 500) o event loop principal ao receber documentos vazados do Dispatcher? Eles devolverão o PDF graciosamente ao status `PENDING_IMPLEMENTATION`? (Não/Necessário programar Fallback Exception Hander em `synapse.py`).
- [ ] Existência de um mecanismo de Rollback de Transação Graph para reverter o `MERGE` de nós caso as conexões `[:ISSUED_BY]` ou `[:CONTAINS]` falhem por corrupção temporal/queda do banco no meio da execução? (Resolvido na V1 de hoje, blocos transaction.begin() cobrem as pontas vulneráveis).

--------------------------------------------------------------------------------

## [2026-03-10T14:30:00Z] — Antecipação V2: Design do NodePersistenceOrchestrator
> Enviado pelo AG para validação do Arquiteto (Claude)

**Proposta (V2):** Criar um orquestrador central e unificado `NodePersistenceOrchestrator` em `src/v3/core/persistence.py`.
O design visa aliviar as Skills (ex: `invoice_skill.py`, `salary_skill.py`) da responsabilidade de executar Cypher. As Skills agora atuarão exclusivamente no plano cognitivo, devendo apenas extrair e retornar uma instância validada de qualquer subclasse de `BaseNode` (ex: `InvoiceData`, `ClientNode`, `SalarySlipNode`).

**Contrato de Interface e Responsabilidades do Orquestrador:**

---

## 👁️ VISÃO DE PRODUTO: MENIR MCP GATEWAY (Inteligência Invisível)

**Data da Análise:** 2026-03-10
**Status:** Pré-análise de Viabilidade Técnica Concluída.

Arquiteto, confirmei o fingerprint `MENIR-P45-20260310-FASE45_ORCHESTRATOR`. Abaixo está o raio-x focado na conversão do Menir em uma camada unificada de inteligência acionável via IAs externas (ChatGPT, Claude).

### Ponto 1: Raio-X Atual (`server.py` e `security.py`)
O que já temos e a distância para o Gateway:

*   **O que já existe:**
    *   Servidor `FastMCP` de pé (`src/v3/mcp/server.py`).
    *   3 Ferramentas expostas (`get_strict_schema`, `search_logs`, `check_quarantine_reasons`, `explain_node`).
    *   Filtro básico de PII no `security.py` (Classe `PiiFilter` intercepta chaves como `cpf`, `salary`).
    *   Conexão Read-Only delegada para um usuário Neo4j isolado (`ai_reader`).
*   **O que é STUB / Ausente (Distância para o Alvo):**
    *   **Autenticação JWT/Bearer:** Inexistente. O `server.py` inicializa aberto (via `stdio`). Não existe camada de interceptação HTTP (SSE com token validation) pronta para Cloud.
    *   **Isolamento Galvânico:** As ferramentas atuais (`check_quarantine_reasons`) **não recebem nem injetam** o Tenant atual no `TenantContext.get()`. A Ana Caroline leria as quarentenas da BECO se estivessem no mesmo banco.
    *   **Auditoria Ativa Opcional/Zero:** O `MCPQueryGuard` citado no seu descritivo **nem sequer existe** no `security.py` hoje. As IAs acessam dados, mas não deixam rastros formais em nós `(:AuditLog)` no grafo informando quem, quando e o quê.
    *   **Transporte Externo:** FastMCP hoje opera localmente. Para ChatGPT e CustomGPTs, precisamos transacionar o MCP Server para subir via SSE (`FastMCP.run_sse()`) atrelado à porta do FastAPI/Uvicorn.

### Ponto 2: Design Semântico (As Funções Alvo)
Nenhuma menção a Cypher. Apenas Verbos de Negócio blindados pelo Tenant injetado no Gateway.

1.  **`minhas_faturas_pendentes()`**
    *   *Descrição:* Lista invoices ativas que estão aguardando aprovação humana ou reconciliação Zefix.
    *   *Nós Consultados:* `(i:Invoice)-[:BELONGS_TO_TENANT]->(:Tenant) WHERE i.status = "PENDING"`
    *   *Retorno AI:* Lista JSON limpa com Fornecedor, Data, Valor Bruto.
2.  **`alertas_ativos(prioridade: str = "ALTA")`**
    *   *Descrição:* Traz Documentos em QUARANTINE e discrepâncias de Tax rates dos últimos 3 dias.
    *   *Nós Consultados:* `(:Document {status: 'QUARANTINE'})`, Erros OGM.
    *   *Retorno AI:* Array narrativo dos problemas priorizados.
3.  **`pulso_dos_projetos(janela_dias: int = 15)`**
    *   *Descrição:* Calcula quais projetos (`:Project`) não recebem links novos (notas, assets, reuniões) dentro da janela.
    *   *Nós Consultados:* `(:Project)-[:HAS_ACTIVITY]->()`
    *   *Retorno AI:* Ranking "Estável/Atenção/Crítico" de projetos.
4.  **`resumo_diario_fiscal()`**
    *   *Descrição:* Sumário da carga de trabalho para peritos Fiduciários (Nicole).
    *   *Nós Consultados:* Contagem global de novos `ClientNode`, `TaxDossierNode` inseridos nas últimas 24h.
    *   *Retorno AI:* Métricas contábeis agregadas para relatório matinal.
5.  **`check_vendor_trust_score(vendor_name: str)`**
    *   *Descrição:* Verifica imediatamente o grau de confiança de um fornecedor (Zefix Cache).
    *   *Nós Consultados:* `(v:Vendor)`
    *   *Retorno AI:* { match: bool, status: string, ultimo_uso: date }
6.  **`mapa_de_ideias_recente()`**
    *   *Descrição:* Para criadores (Ana Caroline). Retorna os 5 Documentos de Brainstorming (texto puro/áudio da semana passada) conectados no Grafo.
    *   *Nós Consultados:* `(:DocumentConcept)-[:MENTIONS]->(:Concept)`
    *   *Retorno AI:* Grafo JSON das tags orbitando os insights da semana.
7.  **`meus_prazos_fiscais_criticos()`**
    *   *Descrição:* Busca declaracoes (ex: TVA) conectadas a datas limites iminentes (< 14 dias).
    *   *Nós Consultados:* `(:TaxDossierNode)`, `(:TVADeclarationNode)`
    *   *Retorno AI:* Lista de Clientes e Dossiês pendentes de envio.
8.  **`solicitar_draft_justificativa(invoice_id: str)`**
    *   *Descrição:* Caso uma fatura apresente *Tips* altos ou problemas, a IA puxa os dados e sugere um rascunho.
    *   *Nós Consultados:* `(:Invoice {uid: X})<-[:ISSUED_BY]-(:Vendor)`
    *   *Retorno AI:* Contexto Fiduciary-Rich para LLM gerar e-mail.

### Ponto 3: O Watchdog Proativo
O pulso não depende da IA e vive nos bastidores. Como orquestrar?

*   **A Abordagem:** Misturar *Cronjobs Python separados* com a API gera código espalhado. Como já o Menir tem uma espinha dorsal síncrona/assíncrona robusta rodando FastAPI (Sinergis), a integração do **APScheduler rodando na mesma thread do Uvicorn (FastAPI scheduler)** é, disparado, a melhor arquitetura.
*   **A Mecânica:** A startup do `synapse.py` daria boot também no APScheduler.
    *   **Resumo Diário (Cron: 08:00):** Monta dict de Tenants ativos, roda queries de delta das últimas 24h, agrupa e dispara notificação (Telegram API / Bot).
    *   **Alerta de Quarentena (Evento-Driven):** Não precisa de scheduler! Altera-se pontualmente a função `_quarantine_document` da `InvoiceSkill` e do `Dispatcher` para injetarem na fila assíncrona o Webhook de Telegram instantes após rodar a query de status.
    *   **Pulso Semanal (Cron: Seg 07:00):** Itera na lista de nodos Project pelo tenant ativo.

### Ponto 4: Autenticação Multi-Tenant Externa (Zero-Trust Context)
Como as IAs externas falarão conosco sem quebrar isolamento?

1.  **Transport Layer:** Em vez de `stdio` MCP, criaremos endpoints `HTTP SSE` (via `starlette/fastapi`) em `/mcp/`).
2.  **Bearer Token Assimétrico:** O Menir OS emite um Token Estático Long-Lived para o perfil "Nicole-BECO". O token carrega apenas ID encriptado.
3.  **Auth Middleware (O Gatekeeper):** O ChatGPT manda `Authorization: Bearer <TOKEN>`.
    O middleware do FastAPI intercepta:
    *   Decodifica Token -> ID do Usuário (Luiz, Nicole, etc).
    *   Vai ao Grafo (Cache Local): Busca Relação `(:User)-[:BELONGS_TO_TENANT]->(:Tenant {name: 'BECO'})`.
    *   **Ponto Chave:** Antes da rota MCP executar, o middleware executa `TenantContext.set("BECO")`.
    *   Todas e quaisquer queries lançadas pelas ferramentas da "Ponto 2" pegarão a string "BECO" com isolamento galvânico garantido, impossibilitando (arquiteturalmente) qualquer injeção do OpenAI.

### 🗺️ Estimativa & Roadmap Incremental (Sessões de Trabalho)

Este mapa não entra em código hoje, mas exige cerca de **4 a 5 Séries de Execução** (Sessões de 3 a 4h cada com o AG):

| Fase | Título Tático | Esforço Base (Sessões) | Foco principal |
|---|---|---|---|
| **Phase 46** | *The Scribe & Cloud Protocol* | 1 a 2 | Transformar `server.py` em SSE HTTP c/ Bearer JWT Middleware integrado ao FastAPI. Emissão de Keys para testes no CustomGPT da OpenAI. |
| **Phase 47** | *The Semantic Sandbox* | 1 | Derrubar a ferramenta `search_logs` solta e injetar as 8 ferramentas semânticas estruturais com `TenantContext` obrigatório. |
| **Phase 48** | *Menir Audit Trail* | 1 | Codar o Middleware `MCPQueryGuard` em `security.py` anotando os nós `(:AuditLog)` no grafo após cada callback das ferramentas (Grafo rastreável por LLMs). |
| **Phase 49** | *The Invisible Watchdog* | 1 a 2 | Trazer as credenciais do `Telegram Bot` pra dentro e programar o Event-Driven Quarentena + APScheduler matinal integrado na instância FastAPI. |

Aguardando deliberações sobre a Fase 46.

## [2026-03-10T17:15:00Z] — Resultados E2E Post-Sanitização e Auditoria V1
> Enviado pelo AG para o Arquiteto / Luiz

Conforme solicitado, rodamos o Smoke Test completo e realizamos a varredura nos 5 nós centrais.

### 1. Placar Binário do Smoke Test E2E (MENIR_INVOICE_LIVE=true)
O teste avançou a Camada do Dispatcher perfeitamente, entretanto falhou na persistência Neo4j por um detalhe de configuração de Banco vs Free Tier.
- **[PASS] CLASSIFICACAO:** Tipo de Fatura com Alta Confianca (Facture, Confiança 0.99)
- **[FAIL] PROCESSAMENTO SKILL:** Falhou: `Neo.ClientError.Database.DatabaseNotFound - Unable to get a routing table for database 'neo4j' because this database does not exist`.
- **[FAIL] NEO4J INVOICE:** No Invoice ausente
- **[FAIL] NEO4J RASTREABILIDADE:** Aresta DERIVED_FROM inexistente
- **[FAIL] NEO4J ZEFIX:** Relacao ISSUED_BY ou Vendor ausente

*Causa Raiz:* O driver driver do SDK do Python tentou conectar com o default `database='neo4j'`, mas a instância AuraDB Free Tier só permite acesso via o banco base hardcoded via User Name (ex: `7ac789d0`). 

### 2. Sanitização de Código (Varredura nas 3 Categorias)

**A) Strings Hardcoded que deveriam ser variáveis de ambiente:**
1. `synapse.py` (Linhas 172-175): Acesso via mock authentication literal, hardcoded, gravíssima: `username == "beco" and password == "admin"`.
2. `synapse.py` (Linha 208): A chave de token JWT é um valor hardcoded como fallback que vaza publicamente a segurança do cluster -> `"super_secret_menir_key_2026"`.
3. `invoice_skill.py` (Linha 67): API URL do Zefix não atrelada ao environment variable (`"https://www.zefix.admin.ch/..."`).

**B) Comentários ou Logs expondo PII / Dados Sensíveis:**
1. `invoice_skill.py` (Linha 263-264): Quando ocorre um ValidationError fiduciário nativo, a skill injeta `e.json()` de forma crua dentro do `inject_entropy_anomaly` no Grafo. Isso grava permanentemente as informações sensíveis originais em texto plano antes do sanitizador atuar de vez.
2. O `sanitizer.py` mascara corretamente os logs (`[TOKEN_AVS_...]`). Não há falhas aparentes de vaza nele.

**C) Caminhos de erro retornando Stack Traces Físicas aos usuários finais:**
1. `persistence.py` (Linhas 26, 34, 42): Levanta exceções físicas como `ValueError` e `OrphanNodeError` crus de volta para sub-camadas das Skills, furando bolhas de encapsulamento com um erro HTTP/Stacktrace feio pro frontend.
2. `invoice_skill.py` (Linhas 134 e 276): Na cláusula Catch-All de Pydantic fallback, engloba tudo num "message=str(e)". O pacote devolve ao frontend o ClientError inteiro do Neo4j e caminhos de drivers internos, vazando a infra da Menir pro mundo exterior.

### 3. Parecer Técnico para o Arquiteto: Top 3 Riscos Residuais
Minha predição antes da virada com ambiente real para a Fiduciária.

1. **Risco Crítico Extraordinário: `synapse.py`**. O entry point global do cluster inteiro. As senhas "admin" mockadas e o fallback "super_secret_menir_key_2026" abrem o cofre via CURL ou via postman caso vaze na build em Cloud. O isolamento cai por terra 100%. 
2. **Risco Crítico Backend: `persistence.py`**. Desaba em Raw 500 Errors. A UI Web capotará totalmente se uma aresta de relacionamento der erro porque o sistema não captura falhas de Constraints para devolver um 400 Bad Request limpo JSON.
3. **Risco Médio Vazamento: `invoice_skill.py`**. A injeção da entropia na linha de Validation Errors arquiva os valores reais em JSON no Neo4j como string limpa, contornando o Sanity Tokenizer. Além de misturar StackTraces no Object Array (que causou justamente a visibilidade do nosso erro no output do teste final E2E).
