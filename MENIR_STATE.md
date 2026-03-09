> Arquivo de Sincronização — Lido por Claude (Arquiteto) e AG (Executor) no início de TODA sessão.
> Localização canônica: raiz do repo `/Menir/MENIR_STATE.md`
> Cópia espelho: `~/.gemini/antigravity/brain/MENIR_STATE.md`

---

## 🔑 FINGERPRINT DE SESSÃO
```
MENIR-P44-20260309-SPRINT_1B_DONE
```
- AG: anuncie este fingerprint ao iniciar sessão.
- Claude: confirme antes de qualquer instrução.
- Divergência → parar e sincronizar antes de trabalhar.
- Formato: `MENIR-P{fase}-{YYYYMMDD}-{LAST_TASK_SLUG}`

---

## 📍 FASE ATUAL
- **Fase:** 44
- **Etapa:** Enterprise Dashboard + Swiss-Clinical CSS Modular Shell
- **Status:** Pré-condições completas. mypy 53→21 (5 residuais em menir_intel — stubs apenas).
- **Próxima execução:** invoice_skill.py lógica real suíça → depois Fase 44 Dashboard

---

## ✅ CONCLUÍDO (sessão 05/03/2026)

| # | O que foi feito |
|---|----------------|
| ✅ | `vertexai` removido de `menir_intel.py` |
| ✅ | `identity.py` ContextVar[str\|None] corrigido |
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
| ✅ | SPRINT 1A: Infra Base (postbox/, scripts de health scan/log, git hooks) |
| ✅ | SPRINT 1B: Health Scan calibrado para SESSION_BRIEF |

---

## 🚨 BLOQUEADORES ATIVOS

| ID | Arquivo | Problema | Risco |
|----|---------|---------|-------|
| R1 | `menir_intel.py` | 5 erros mypy residuais (stubs/Any — não crasham) | 🟡 RUÍDO |
| R2 | `protools.py:11` | `STRICT_SCHEMA` inexistente no graph_schema | 🟠 MCP QUEBRADO |
| R3 | `meta_cognition.py:36` | `auth` implicit Optional | 🟡 TYPE HINT |
| R4 | `invoice_skill.py` | Sem lógica real de extração suíça | 🔴 REVENUE BLOCKER |
| R5 | Dashboard | Zero UI para BECO e Ana | 🟠 FASE 44 |

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
mypy errors:            21 residuais (5 em menir_intel stubs, resto type hints)
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
[ ] invoice_skill.py: lógica real de extração suíça (BECO revenue blocker)
[ ] FASE 44: Enterprise Dashboard shell React
[ ] FUTURO: AudioSkill (WhatsApp → Gemini Audio → LeadSkill)
[ ] FUTURO: TrustScore dinâmico
```

---

## 🏗️ VERDADES IMUTÁVEIS

```
1. ContextVar é única fonte de verdade de tenant — jamais parâmetro de função
2. extra="forbid" em schemas de ENTRADA de LLM
3. extra="allow" SOMENTE em OGM de saída do grafo
4. asyncio.to_thread() para todo I/O síncrono em contexto async
5. Todo nó DEVE ter [:BELONGS_TO_TENANT]
6. BECO = fiduciária suíça | SANTOS = pessoal/Ana Caroline
7. Confiar no repo quando contradizer documentação
8. BECO é prioridade de receita — runway limitado
9. (:Menir) e (:User) são os dois nós raiz — meta-camada acima dos tenants
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

*Gerado por: Claude (Arquiteto Principal) | 05/03/2026*
*Corpo e fingerprint sincronizados — sessão completa registrada*
