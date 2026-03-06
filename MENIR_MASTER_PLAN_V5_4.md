# MENIR OS — PLANO MESTRE DE EVOLUÇÃO
> Documento canônico de arquitetura e execução progressiva
> Versão: V5.4 | Atualizado: 06/03/2026 | Autoria: Claude (Arquiteto Principal)
> Para: AG (Executor) | Leitura obrigatória antes de qualquer execução

---

## ESTADO REAL DO SISTEMA (06/03/2026)

```
Fingerprint:    MENIR-P44-20260305-MENIR_INTEL_SEALED
mypy errors:    65 (22 arquivos, 36 verificados)
Neo4j:          Aura Free — conectado
Tenants:        BECO, SANTOS — ativos
Frontend:       React + Vite + TS — Auth Bridge ativo
invoice_skill:  estrutura ok — travada por MENIR_INVOICE_LIVE=false
```

---

## CONTEXTO — O QUE O MENIR É AGORA

O Menir não é mais apenas um kernel financeiro para BECO e SANTOS.
É um **Cognitive Personal OS** que qualquer pessoa pode instalar para si.
BECO e SANTOS são instâncias de um padrão mais genérico.

```
Luiz hoje:    BECO (fiduciária suíça) + SANTOS (vida pessoal)
Novo usuário: CONTABIL (financeiro)   + PESSOAL (vida pessoal)
```

O código não muda. O bootstrap muda.

**Mantra:**
> "Data acts as a vector; logic acts as a scalar.
>  Only the Graph Remembers — and it remembers *you*."

---

## PRINCÍPIOS INVIOLÁVEIS

```
1.  ContextVar é a única fonte de verdade de tenant — jamais parâmetro de função
2.  extra="forbid" em schemas de ENTRADA de LLM
3.  extra="allow" SOMENTE em OGM de saída do grafo
4.  asyncio.to_thread() para todo I/O síncrono em contexto async
5.  Todo nó Neo4j DEVE ter [:BELONGS_TO_TENANT]
6.  BECO/SANTOS = instâncias. CONTABIL/PESSOAL = padrão genérico.
7.  Confiar no repo quando contradizer documentação
8.  BECO é prioridade de receita — runway limitado
9.  (:Menir) e (:User) são os dois nós raiz — meta-camada acima dos tenants
10. menir_capture: nunca mais de UMA pergunta por input
11. menir_capture: a pergunta usa o grafo — nunca é genérica
12. Grafo pessoal (V0): Luiz decide o que entra. AG nunca escreve sozinho.
13. AG é reativo, não daemon — executa quando chamado, não em background
14. Velocidade 1: AG notifica depois. Velocidade 2: AG propõe antes.
```

---

## MODELO DE AUTONOMIA DO AG — CONTRATO DEFINITIVO

### VELOCIDADE 1 — AG Executa Sem Autorização
```
✅ Fixes mypy tipo hints, implicit Optional, Sequence→list
✅ requirements.txt, py.typed, README cosmético
✅ Scripts de infra (postbox, sync, health scan)
✅ Refactor dentro de UM único módulo sem mudar contratos públicos
✅ SessionLog no Neo4j (metadados de sessão)
✅ Smoke tests que passam isoladamente
✅ Aliases, git hooks, scripts de conveniência

→ Notificar DEPOIS em menir-postbox/completed-ag.md
→ Commit: "fix: <descrição>" ou "chore: <descrição>"
```

### VELOCIDADE 2 — AG Propõe, Arquiteto Valida
```
🟠 Mudança de contrato entre módulos (assinatura de função pública)
🟠 Nova relação no grafo Neo4j (qualquer tenant)
🟠 Fix que envolve 2+ módulos simultaneamente
🟠 Qualquer toque em menir_bridge.py (isolamento galvânico)
🟠 Lógica de negócio BECO (TVA, compliance, Crésus output)
🟠 Mudança de modelo LLM ou embedding
🟠 Novos schemas Pydantic

→ Escrever em menir-postbox/inbox.md e AGUARDAR
→ Claude responde em menir-postbox/decisions.md
→ Executar só após "✅ AUTORIZADO" no decisions.md
```

### VELOCIDADE 0 — Luiz Presente Obrigatório
```
🔴 Qualquer nó do grafo pessoal (:User, :BirthChart, :Decision, :Insight)
🔴 Relações de família, colaboradores, projetos de vida
🔴 Dados de produção BECO (faturas reais, transações)
🔴 Schema de InvoiceData / compliance suíça em produção
🔴 Prioridade estratégica entre BECO e outras camadas
🔴 Onboarding de novo usuário

→ Nenhum código roda. Nenhum commit. Nenhum Cypher.
→ Sinalizar no inbox.md + aguardar sessão com Luiz presente.
```

---

# EXECUÇÃO ATUAL — CORREÇÃO DE ERROS MYPY

## ESTADO: 65 erros em 22 arquivos

Distribuição por arquivo (06/03/2026):
```
menir_intel.py          9 erros
core/menir_runner.py    7 erros
skills/invoice_skill.py 6 erros
skills/lead_skill.py    5 erros
mcp/server.py           5 erros
extensions/astro/__init__.py  4 erros
mcp/protools.py         3 erros
meta_cognition.py       3 erros
menir_bridge.py         3 erros
core/synapse.py         3 erros
skills/camt053_skill.py 2 erros
core/reconciliation.py  2 erros
extensions/astro/genesis.py   2 erros
mcp/test_mcp_tools.py   2 erros
core/embedding_service.py     2 erros
core/protocols.py       1 erro
core/sanitizer.py       1 erro
core/provenance.py      1 erro
extensions/astro/schema.py    1 erro
core/logos.py           1 erro
mcp_server.py           1 erro
core/neo4j_pool.py      1 erro
```

---

## BATCH 1 — RUÍDO ESTRUTURAL (V1 — AG executa agora)
**Estimativa: 15min | Zero risco de regressão**

Objetivo: eliminar erros de stubs ausentes via configuração — sem tocar em código.

Adicionar ao `mypy.ini` os seguintes blocos de override:

```
[mypy-flatlib.*]
ignore_missing_imports = True

[mypy-aiofiles.*]
ignore_missing_imports = True
```

Isso elimina todos os erros de import-not-found de flatlib e aiofiles
sem modificar nenhum arquivo Python.

Após executar: rodar mypy e reportar nova contagem.
Commit: `chore: mypy.ini suppress flatlib and aiofiles stubs`

---

## BATCH 2 — IMPLICIT OPTIONAL BATCH (V1 — AG executa agora)
**Estimativa: 30min | Zero risco de regressão**

Objetivo: corrigir o padrão `argumento: str = None` → `argumento: str | None = None`
em todos os arquivos afetados. É o erro mais comum e mais seguro de corrigir.

Arquivos e localizações exatas:

**mcp/security.py** — argumento `allowed_fields`
Tornar explicitamente Optional.

**core/provenance.py** — argumento `target_node_id`
Tornar explicitamente Optional.

**mcp/protools.py** — argumento `keyword` + 2 erros `Returning Any`
Tornar `keyword` explicitamente Optional.
Para os `Returning Any`: adicionar `cast(dict[str, Any], resultado)`.

**mcp/server.py** — argumento `keyword`
Tornar explicitamente Optional.

**menir_intel.py** — argumento `api_key`
Tornar explicitamente Optional.

**menir_intel.py** — argumento `image_path` e `few_shot_examples`
Tornar explicitamente Optional.

**core/synapse.py** — variável `command_bus` sem anotação
Adicionar anotação de tipo: `dict[str, Any]`.

**core/reconciliation.py** — variável `payload` sem anotação
Adicionar anotação de tipo: `dict[str, Any]`.

**meta_cognition.py** — `Sequence[str]` com `.append()`
Trocar `Sequence[str]` por `list[str]` nas linhas 169 e 180.

**meta_cognition.py** — `session.run()` com `**dict`
Passar `parameters=dict(params)` em vez de `**params`.

Após executar: rodar mypy e reportar nova contagem.
Commit: `fix: implicit Optional batch + Sequence→list + type annotations`

---

## BATCH 3 — SDK MORTA + CONTRATOS (V2 — Aguarda Arquiteto)
**Estimativa: 45min | Envolve 2+ módulos**

AG deve escrever proposta no inbox.md antes de executar.

Itens pendentes de autorização:

**menir_intel.py — SDK google.generativeai (EOL Nov/2025)**
Linha 14: import ainda presente.
Linhas 66 e 224: uso ativo no path de produção.
AG deve propor como remover sem quebrar o fallback de persona.

**core/logos.py — Literal type incompatível**
Linhas 108 e 146: origem sendo setada como str genérica
em vez de Literal restrito.

**core/menir_runner.py — argumentos de MenirOntologyManager**
Linha 242: tipos incompatíveis na chamada do construtor.
Envolve menir_runner.py + meta_cognition.py — dois módulos.

**menir_bridge.py — tenant_id como parâmetro (violação galvânica)**
6 métodos recebem tenant_id como parâmetro de função.
Princípio inviolável #1 violado.
AG propõe migração para leitura via ContextVar.

---

## BATCH 4 — INVOICE SKILL RUNTIME (V0 — Luiz presente)
**Estimativa: 2h | Toca em compliance BECO**

Atenção: o invoice_skill.py tem a estrutura de extração pronta.
O bloqueio principal é `MENIR_INVOICE_LIVE=false` no ambiente.

Bugs de runtime identificados (não aparecem no mypy):

**Bug 1:** Comentários `# noqa: W293` dentro da string Cypher.
O Neo4j recebe esses comentários como texto da query e rejeita.

**Bug 2:** `vendor_uid` presente nos parâmetros mas ausente na query Cypher.

**Bug 3:** Validação Swiss UID MOD11 ausente no schema InvoiceData.

**Bug 4:** `MENIR_INVOICE_LIVE=true` não está definido no .env do BECO.

Sequência de execução deste batch:
1. Luiz confirma que está presente
2. AG limpa a query Cypher (Bug 1 + Bug 2)
3. AG adiciona validador MOD11 ao schema InvoiceData
4. Luiz define MENIR_INVOICE_LIVE=true no .env
5. Teste com fatura fixture (não produção)
6. Validação: Swiss UID passa MOD11, TVA é 8.1%/3.8%/2.6%

---

# CAMADA 1 — WORKFLOW CLAUDE ↔ AG

## SPRINT 1A — Infra Base (pendente)
**Objetivo:** Eliminar upload manual de MENIR_STATE.md para sempre.
**Estimativa:** 3-4h | **Risco:** V1

Passos:
1. Criar estrutura `menir-postbox/` na raiz do repo com 4 arquivos:
   - inbox.md (AG escreve quando precisa de decisão)
   - decisions.md (Claude escreve autorizações)
   - completed-ag.md (AG reporta execuções V1)
   - todo-ag.md (tarefas autorizadas pendentes)

2. Criar `scripts/menir_health_scan.py`
   Verifica: mypy count, SDKs mortas, arquivos de risco modificados,
   Neo4j health, classifica tudo em V1/V2/V0, gera SESSION_BRIEF.md.

3. Criar `scripts/log_session_to_graph.py`
   Registra :SessionLog no Neo4j após cada commit.
   Conecta a (:User {uid:"luiz"}) e (:Menir {uid:"MENIR_CORE"}).

4. Criar `.git/hooks/post-commit`
   Dispara automaticamente: brain sync + Drive upload + health scan + Neo4j log.

5. Criar `~/menir_aliases.sh`
   Aliases: menir-status, menir-brief, menir-sync, menir-checkpoint, menir-resolve.

6. Criar `CLAUDE.md` na raiz do repo
   20 linhas com fingerprint atual, fase, modelo de autonomia resumido.
   Lido automaticamente pelo AG no início de toda sessão.

7. Configurar Google Drive sync
   Criar pasta "Menir Sync" no Drive, exportar MENIR_DRIVE_FOLDER_ID.
   gdrive CLI autenticado.

Verificação final:
- menir-status mostra fingerprint correto
- git commit dispara post-commit hook
- SESSION_BRIEF.md aparece no Drive automaticamente
- Luiz não faz upload de nada

## SPRINT 1B — Health Scan calibrado
**Objetivo:** SESSION_BRIEF com proposta inteligente por sessão.
**Estimativa:** 2h | **Risco:** V1

Arquivos de risco a classificar no scan:
```
menir_bridge.py     → V2 (galvânico)
identity.py         → V2 (tenant isolation)
invoice_skill.py    → V0 (BECO revenue)
cresus_exporter.py  → V0 (BECO compliance)
reconciliation.py   → V2 (BECO finance)
genesis.py          → V0 (grafo pessoal)
```

## SPRINT 1C — Neo4j SessionLog
**Objetivo:** Grafo como memória permanente de sessões.
**Estimativa:** 1h | **Risco:** V1

Schema no Neo4j:
```
(:SessionLog {fingerprint, phase, date, commit_hash,
              files_modified, mypy_count, tasks_completed})

(u:User)-[:HAD_SESSION]->(s:SessionLog)
(m:Menir)-[:LOGGED]->(s:SessionLog)
(s:SessionLog)-[:HAS_BLOCKER]->(b:Blocker)
```

---

# CAMADA 2 — AMBIENT GRAPH INGESTION

## O QUE É

Luiz fala naturalmente. Menir extrai entidades, consulta o grafo,
faz UMA pergunta informada pelo grafo, e registra no Neo4j.

```
"conheci a Sarah hoje na faculdade"
       ↓
Gemini extrai: Person=Sarah, Institution=faculdade
       ↓
Neo4j consulta: Luiz frequenta qual instituição?
       ↓
Menir pergunta: "Sarah é da UNIP Santos ou de outra instituição?"
       ↓
Luiz responde → Neo4j registra com certeza alta
```

**Regra fundamental:** nunca mais de UMA pergunta por input.
A pergunta é sempre formulada com contexto do grafo — nunca genérica.

## SPRINT 2A — menir_capture.py (V2 — schema a validar)

AG deve propor o schema completo do domínio PESSOAL no inbox.md
antes de escrever qualquer código. Arquiteto valida os labels e
relações antes da implementação.

Labels propostos: Person, Project, Institution, LifeEvent, Insight, Goal
Relações propostas: MET, COLLABORATES_WITH, STUDIES_AT, WORKS_AT,
                    EXPERIENCED_EVENT, HAD_INSIGHT, HAS_GOAL

Todos os nós PESSOAL devem ter [:BELONGS_TO_TENANT]->(:Tenant {name:"PESSOAL"})

## SPRINT 2B — TrustScore em Pessoas (V1)

TrustScore de 0.0 a 1.0 baseado em:
- interactions_count (incrementa a cada capture)
- contexts distintos onde a pessoa aparece
- tempo desde first_met_date
- is_real flag

---

# CAMADA 3 — BECO REVENUE UNLOCK

## ⚠️ PRIORIDADE MÁXIMA — RUNWAY LIMITADO

Camada 3 tem precedência sobre Camada 2 se o runway apertar.

## SPRINT 3A — invoice_skill.py ativo (2h — não 6h)

A extração suíça já existe. O bloqueio é operacional, não técnico.
Ver Batch 4 acima para sequência exata.

O que precisa funcionar para BECO operar:
- Query Cypher limpa (sem comentários Python dentro)
- Swiss UID MOD11 validando
- MENIR_INVOICE_LIVE=true no .env
- Teste com fatura fixture aprovado

## SPRINT 3B — Dashboard Fase 44 (V2 — após 3A)

Desbloqueado pelo Sprint 3A. Dashboard sem dados reais = UI vazia.

MVP mínimo:
- Listagem de faturas BECO com status
- Valor total do período
- Link para export Crésus

## SPRINT 3C — AudioSkill WhatsApp (V2 — futuro)

```
WhatsApp Audio → Webhook → Gemini Audio → Transcrição
                                               ↓
                                    LeadSkill / InvoiceSkill / menir_capture
```

---

# CAMADA 4 — MENIR PARA OUTROS USUÁRIOS

Bootstrap genérico: qualquer novo usuário recebe CONTABIL + PESSOAL.
Cypher idempotente via MERGE para criação de User + dois Tenants.
Luiz mantém BECO + SANTOS por razão histórica — sem mudança no código.

---

# SEQUÊNCIA DE EXECUÇÃO — ORDEM ABSOLUTA

```
AGORA (V1 — AG executa sem autorização):
  [ ] Batch 1: mypy.ini — suprimir flatlib + aiofiles
  [ ] Batch 2: implicit Optional em 10 localizações
  [ ] Rodar mypy e reportar nova contagem ao Arquiteto

PRÓXIMO (V2 — AG propõe no inbox.md):
  [ ] Batch 3: SDK morta + logos.py + menir_runner.py + bridge galvânico
  [ ] Sprint 1A: estrutura postbox + scripts + git hooks + Drive sync

LUIZ PRESENTE (V0):
  [ ] Batch 4: invoice_skill runtime bugs + MENIR_INVOICE_LIVE=true
  [ ] Sprint 2A: validar schema PESSOAL antes do menir_capture.py

APÓS BECO OPERANTE:
  [ ] Sprint 3B: Dashboard Fase 44
  [ ] Sprint 2B: TrustScore em pessoas
  [ ] Sprint 3C: AudioSkill WhatsApp
  [ ] Camada 4: bootstrap genérico CONTABIL/PESSOAL
```

---

## PROTOCOLO DE SESSÃO

Ao iniciar qualquer sessão:
1. AG anuncia fingerprint do MENIR_STATE.md local
2. Claude confirma contra o Project
3. Divergência → sincronizar antes de qualquer execução
4. AG lê inbox.md — há itens pendentes de decisão?
5. Apenas então: executar

Ao concluir tarefa:
1. Atualizar MENIR_STATE.md com novo fingerprint
2. Formato: MENIR-P{fase}-{YYYYMMDD}-{TASK_SLUG}
3. git commit + copy para brain
4. Luiz re-sobe no Claude Project

---

*Versão V5.4 | Atualizado: 06/03/2026*
*Incorpora: contagem real de 65 erros, Batches 1-4, Sprint 3A corrigido para 2h*
*Fingerprint de referência: MENIR-P44-20260305-MENIR_INTEL_SEALED*
