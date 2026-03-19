> Arquivo de Sincronização — Lido por Claude (Arquiteto) e AG (Executor) no início de TODA sessão.
> Localização canônica: raiz do repo `/Menir/MENIR_STATE.md`
Arquivo de Sincronização — Lido por Claude (Arquiteto) e AG (Executor) no início de TODA sessão.
Localização canônica: raiz do repo `/Menir/MENIR_STATE.md`
Cópia espelho: `~/.gemini/antigravity/brain/MENIR_STATE.md`

---

## 🔑 FINGERPRINT DE SESSÃO
```
MENIR-P46-20260319-TASK7_COMPLETE
```
- AG: anuncie este fingerprint ao iniciar sessão.
- Claude: confirme antes de qualquer instrução.
- Divergência → parar e sincronizar antes de trabalhar.
- Formato: `MENIR-P{fase}-{YYYYMMDD}-{LAST_TASK_SLUG}`

---

## 📍 FASE ATUAL
- **Fase:** 46
- **Etapa:** Step 4 (BECO Fixture - Swiss Ingestion - Abismo 0 Fully Resolved)
- **Status:** Etapa 4 concluída. Pipeline QR, Sanitização, Dashboard de Quarentena e Exportação Crésus validados.
- **Dívida Técnica Pendente:** TECH_DEBT_NEO4J_ASYNC (Driver async nativo postergado para Fase 46).

---

### Status Atual (Sessão Atual)
- [x] **Fase 46 - Etapa 0**: Setup das novas regras de V2 (Pesquisa Perplexity e Mockup Visual) registradas em `_gemini.md`.
- [x] **Fase 46 - Etapa 1**: Remoção de containers Zumbis (`competent_wescoff`, `vigorous_black`). Validação watcher.py e classificador PDF.
- [x] **Fase 46 - Etapa 2**: Atualização do `src/v3/core/pdf_parser.py` eliminando blocos síncronos IO-bound. Validação do `test_pdf_parser.py`.
- [x] **Fase 46 - Etapa 3**: Refatoração do `src/v3/skills/pdf_classifier.py` eliminando PyMuPDF/fitz.
- [x] **Fase 46 - Etapa 4**: Integração Pyzbar/Pypdfium2 no Neo4j/Gemini Pipeline.
  - [x] **Tarefa 0-3**: QR Extractor e `invoice_skill.py`.
  - [x] **Tarefa 4**: Sanitização de Clientes (`sanitize_clients.py`) com validação MOD97-10.
  - [x] **Tarefa 5**: Bootstrap de Clientes BECO (`bootstrap_beco_clients.py`) com injeção UNWIND Cypher.
  - [x] **Tarefa 6**: Echo Test (`run_echo_test.py`) com PDFs sintéticos e relatório `echo_report_beco.json`.
  - [x] Tarefa 7: Produção & Integração (REST API + Persistência + Prompt v2)
    - [x] 7.1: Endpoint REST `POST /api/classify/document` (TDD)
    - [x] 7.2: Prompt v2 (12 tipos) + Validação DocumentClassification (TDD)
    - [x] 7.3: Persistência Nó `(:Document) ou (:QuarantineItem)` com `origin` (TDD)
    - [x] 7.4: TrustScore Engine (Calculated Confidence)
    - [x] 7.5: Dynamic Routing (Fast Lane vs Quarantine)
    - [x] 7.6: TDD Cycle — 100% coverage for routing logic
  - [x] **Tarefa 8**: Dashboard de Quarentena Premium & Promoção de Nós.
  - [x] **Tarefa 9**: Fix Crésus Export (204 No Content).
  - [x] **Tarefa 10**: Fix post-commit blocking hooks (Background - Reinforced with Windows Detach).
  - [x] **Tarefa 11 (Step 8/9)**: Question Engine (SANTOS) Refined & Integrated with async IO and user_uid context.

---

## ✅ CONCLUÍDO (sessões 05/03/2026 → 17/03/2026)

| # | O que foi feito |
|---|----------------|
| ✅ | `vertexai` removido de `menir_intel.py` |
| ✅ | `identity.py` ContextVar[str|None] corrigido |
| ✅ | `_gemini.md` extra="allow/forbid" resolvido: forbid em entrada LLM, allow em OGM saída |
| ✅ | `genesis.py:92` Person() kwargs → metadata{} |
| ✅ | `cresus_exporter.py:55` return path corrigido |
| ✅ | Implicit Optional em batch (7 arquivos) |
| ✅ | `menir_intel.py:219` get_model → client.models.get() |
| ✅ | `menir_intel.py:116` embed None-guard + fallback [] |
| ✅ | `menir_intel.py:290` cast GenerateContentResponse antes de .text |
| ✅ | `invoice_skill.py:186` contents → Part.from_text() |
| ✅ | `py.typed` adicionado ao graph_schema |
| ✅ | `flatlib` + `types-aiofiles` em requirements.txt |
| ✅ | Dois nós raiz criados: (:Menir) e (:User {uid:"luiz"}) |
| ✅ | Ontologia pessoal bootstrapped (projetos, colaboradores, família) |
| ✅ | Skill `menir-astro-extension` criada no brain |
| ✅ | Skills `@fastapi-pro` + `@auth-implementation-patterns` instaladas |
| ✅ | Skills proprietárias `menir-*` criadas no brain |
| ✅ | MENIR_STATE.md + MENIR_KERNEL.md deployados no repo e brain |
| ✅ | BATCH 1: `mypy.ini` suppress flatlib and aiofiles |
| ✅ | BATCH 2: implicit Optional batch + Sequence→list + type annotations |
| ✅ | SPRINT 1A: Infra Base Completa (Hard Lock Galvânico, postbox append atômico, scripts, hooks Python) |
| ✅ | SPRINT 1B: Health Scan calibrado para SESSION_BRIEF |
| ✅ | BATCH 3: Refactoring de Runtime concluído (intel, logos, runner, bridge) |
| ✅ | BATCH 4 / SPRINT 2A: Mutação 1 (invoice_skill) e Mutação 2 (menir_capture) |
| ✅ | Plano Mestre V5.5 instanciado e em vigor |
| ✅ | Smoke test 6/6 passou com MOD11 real |
| ✅ | PDF classifier multimodal com três caminhos implementado |
| ✅ | Folder watcher standalone implementado |
| ✅ | Sanitização de segurança nos três arquivos (`synapse`, `persistence`, `invoice_skill`) |
| ✅ | Triangulação ativa no `_gemini.md` |
| ✅ | Análise dos arquivos `.cre` do Crésus concluída |
| ✅ | Análise dos cinco abismos operacionais entre o kernel atual e o produto real |
| ✅ | Relocadas pendências do pdf_classifier com mock de SCANNED, HYBRID e DIGITAL |
| ✅ | Remoção dos containers orfãos (competent_wescoff, vigorous_black) reportados offline |
| ✅ | Nova secção de CAPACIDADES NATIVAS adicionadas ao protocolo `_gemini.md` |
| ✅ | Regra TDD Zona Vermelha adicionada ao `MENIR_ARCHITECT_BRIEF.md` |
| ✅ | Timeout 5s no Neo4j health check do pós-commit (`menir_health_scan.py`) |
| ✅ | Crésus Exporter com TVA Extended Format + idempotência `[:RECONCILED exported=True]` |
| ✅ | **Fase 46 - Etapa 0**: Setup das novas regras de V2 (Pesquisa Perplexity e Mockup Visual) registradas em `_gemini.md`. |
| ✅ | **Fase 46 - Etapa 1**: Remoção de containers Zumbis (`competent_wescoff`, `vigorous_black`). Validação watcher.py e classificador PDF. |
| ✅ | **Fase 46 - Etapa 2**: Atualização do `src/v3/core/pdf_parser.py` eliminando blocos síncronos IO-bound. Validação do `test_pdf_parser.py`. |
| ✅ | **Fase 46 - Etapa 3**: Refatoração do `src/v3/skills/pdf_classifier.py` eliminando PyMuPDF/fitz. |
| ✅ | **Fase 46 - Etapa 4 - Tarefa 0**: Dependências adicionadas (pyzbar, pypdfium2, opencv-python-headless). |
| ✅ | **Fase 46 - Etapa 4 - Tarefa 1**: Validação MOD11 suíça corrigida (MOD97-10 real, ISO 7064) em `swiss_qr_parser.py` e tipos ajustados para Decimal. |
| ✅ | **Fase 46 - Etapa 4 - Tarefa 2**: Módulo assíncrono `qr_extractor.py` implementado para scan das últimas 3 páginas (300 DPI) usando thread pools. |
| ✅ | **Fase 46 - Etapa 4 - Tarefa 3**: Integração do Caminho A (QR_DECODE) e Caminho B (GEMINI_FALLBACK) na `invoice_skill.py`. Traceability persistida no Neo4j com `extraction_path` e `extraction_confidence` atualizando a aresta `BELONGS_TO_TENANT`. TDD implementado. |
| ✅ | **Fase 46 - Etapa 4 - Tarefa 4**: Sanitização de Clientes (`sanitize_clients.py`) com validação MOD97-10. |
| ✅ | **Fase 46 - Etapa 4 - Tarefa 5**: Bootstrap de Clientes BECO (`bootstrap_beco_clients.py`) e relatório JSON. |
| ✅ | **Fase 46 - Step 8**: SANTOS Intelligence Layer — Signal cross-tenant com threshold e decay temporal implementados. |
| ✅ | **Fase 46 - Step 8**: DecisionHub agregando sinais de fontes heterogêneas. |
| ✅ | **Fase 46 - Step 8**: `question_engine.py` — uma pergunta por input baseada em gaps do grafo. TDD com TenantContext. |
| ✅ | **Fase 46 - Step 9**: `menir_capture.py` refinado — user_uid dinâmico via grafo, `_persist_actions` com `asyncio.to_thread`. |
| ✅ | **Fase 46 - Step 9**: Hook pós-commit blindado com `CREATE_NO_WINDOW | DETACHED_PROCESS` no Windows. |

---

## 🚨 BLOQUEADORES ATIVOS

| ID | Arquivo | Problema | Risco |
|----|---------|---------|-------|
| R1 | `invoice_skill.py` | Fixture PDF real da Nicole ainda não processada | 🔴 REVENUE BLOCKER |
| ~~R2~~ | ~~`cresus_exporter.py`~~ | ~~Não revisado contra formato .cre real~~ | ✅ RESOLVIDO — TVA Extended + Idempotência |
| ~~R3~~ | ~~Dashboard~~ | ~~Dashboard de quarentena não validado em browser~~ | ✅ RESOLVIDO — Browser Agent QA ativo |

---

## ✅ ESTADO DO SISTEMA

```
Tenants ativos:         BECO, SANTOS
Neo4j:                  Aura Free — conectado
Nó BECO duplicado:      RESOLVIDO ✅
Nó raiz (:Menir):       CRIADO ✅
Nó raiz (:User luiz):   CRIADO ✅
Frontend (Tier 2):      React + Vite + TS — Auth Bridge ativo ✅
FastAPI:                Confirmado ✅
Embedding model:        gemini-embedding-001 (768-dim) ✅
Inference model:        gemini-2.5-flash ✅
vertexai imports:       REMOVIDOS ✅
mypy errors:            139 residuais
Skills proprietárias:   INSTALADAS ✅
Sync infra:             INSTALADA ✅
```

---

## 📋 PRÓXIMAS TAREFAS (por prioridade)

```
[x] PRÉ: Verificar nó BECO duplicado
[x] PRÉ: pip install flatlib + types-aiofiles
[x] PRÉ: GEMINI_INFERENCE_MODEL = "gemini-2.5-flash"
[x] Crash risks zerados (Phases 9-11)
[x] extra="allow/forbid" resolvido
[x] bootstrap_user_luiz.cypher executado
[x] menir-astro-extension criada
[x] py.typed + requirements.txt atualizados
[x] Sync Infra deployada
[x] menir_intel.py selado (5 residuais são stubs)
[x] invoice_skill.py Part.from_text() corrigido

[ ] R2: protools.py STRICT_SCHEMA — corrigir ou remover referência
[ ] R3: meta_cognition.py:36 auth implicit Optional
[ ] BATERIA: 4 blocos de testes (Neo4j + BECO pipeline + segurança + saúde)
[x] invoice_skill.py: lógica real de extração suíça (Tarefa 3 — QR + Gemini fallback implementados)
[x] FASE 44: Enterprise Dashboard shell React (substituído pelo Dashboard de Quarentena Premium)
[/] FUTURO: AudioSkill (WhatsApp → Gemini Audio → LeadSkill) (Telegram + voz ativo para SANTOS — BECO pendente)
[ ] FUTURO: TrustScore dinâmico
[ ] FUTURO: Conectar DecisionHub ao SESSION_BRIEF
```

---

## 🏗️ VERDADES IMUTÁVEIS

```
1. ContextVar é única fonte de verdade de tenant — jamais parâmetro de função
2. extra="forbid" em schemas de ENTRADA de LLM
3. extra="allow" SOMENTE em OGM de saída do grafo
4. asyncio.to_thread() para todo I/O síncrono em contexto async
5. Todo nó DEVE ter [:BELONGS_TO_TENANT]
6. BECO = fiduciária suíça | SANTOS = domínio pessoal de Luiz
7. Confiar no repo quando contradizer documentação
8. BECO é prioridade de receita — runway limitado
9. (:Menir) e (:User) são os dois nós raiz — meta-camada acima dos tenants
10. menir_capture: nunca mais de UMA pergunta por input
11. menir_capture: a pergunta usa o grafo — nunca é genérica
12. Grafo pessoal (V0): Luiz decide o que entra. AG nunca escreve sozinho.
13. AG é reativo, não daemon — executa quando chamado, não em background
14. Velocidade 1: AG notifica depois. Velocidade 2: AG propõe antes.
15. Hooks sempre em Python — nunca Bash puro no Windows
16. Postbox é append-only — nunca sobrescrever, purgar para Neo4j no flip de fingerprint
```

---

## 🔄 PROTOCOLO DE ATUALIZAÇÃO

Após completar qualquer tarefa:
1. Marcar `[x]` na tarefa acima
2. Atualizar FINGERPRINT: `MENIR-P{fase}-{YYYYMMDD}-{TASK_SLUG}`
3. **Atualizar o corpo inteiro** — não só o fingerprint
4. `git add MENIR_STATE.md && git commit -m "state: P{fase} {TASK_SLUG}"`
5. `copy MENIR_STATE.md ~/.gemini/antigravity/brain/MENIR_STATE.md`
6. Luiz re-sobe o arquivo no Claude Project

---

*Gerado por: Claude (Arquiteto Principal) | 17/03/2026*
*Corpo e fingerprint sincronizados — sessão completa registrada*
