MENIR OS — PLANO MESTRE DE EVOLUÇÃO

Versão: V5.5 | Fechado: 06/03/2026
Autoria: Claude (Arquiteto) + AG (Executor) — co-autoria ratificada
Para: AG (Executor) | Leitura obrigatória antes de qualquer execução


ESTADO REAL DO SISTEMA
Fingerprint:    MENIR-P44-20260305-MENIR_INTEL_SEALED
mypy errors:    65 (22 arquivos, 36 verificados)
Neo4j:          Aura Free — conectado
Tenants:        BECO + SANTOS ativos
invoice_skill:  estrutura ok — travada por MENIR_INVOICE_LIVE=false
Ambiente:       Windows + Git Bash — hooks em Python, não Bash

PRINCÍPIOS INVIOLÁVEIS
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
15. Hooks sempre em Python — nunca Bash puro no Windows
16. Postbox é append-only — nunca sobrescrever, purgar para Neo4j no flip de fingerprint

MODELO DE AUTONOMIA — CONTRATO DEFINITIVO
VELOCIDADE 1 — AG Executa Sem Autorização
✅ Fixes mypy: type hints, implicit Optional, Sequence→list
✅ requirements.txt, py.typed, README cosmético
✅ Scripts de infra (postbox, sync, health scan)
✅ Refactor dentro de UM único módulo sem mudar contratos públicos
✅ SessionLog no Neo4j (metadados de sessão)
✅ Smoke tests que passam isoladamente
✅ Aliases, hooks, scripts de conveniência

→ Notificar DEPOIS em menir-postbox/completed-ag.md
→ Commit: "fix: <descrição>" ou "chore: <descrição>"

VELOCIDADE 2 — AG Propõe, Arquiteto Valida
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

VELOCIDADE 0 — Luiz Presente Obrigatório
🔴 Qualquer nó do grafo pessoal (:User, :BirthChart, :Decision, :Insight)
🔴 Relações de família, colaboradores, projetos de vida
🔴 Dados de produção BECO (faturas reais, transações)
🔴 Schema InvoiceData / compliance suíça em produção
🔴 Prioridade estratégica entre BECO e outras camadas
🔴 Onboarding de novo usuário

→ Nenhum código roda. Nenhum commit. Nenhum Cypher.
→ Sinalizar no inbox.md + aguardar sessão com Luiz presente.

LISTA DE ZONA VERMELHA (arquivos V0 — Hard Lock ativo)
src/v3/skills/invoice_skill.py
src/v3/core/cresus_exporter.py
src/v3/core/reconciliation.py
src/v3/extensions/astro/genesis.py
src/v3/core/schemas/identity.py
src/v3/menir_bridge.py          ← V2, mas na lista por impacto galvânico

EXECUÇÃO IMEDIATA — CORREÇÃO DE ERROS MYPY

BATCH 1 — RUÍDO ESTRUTURAL
Velocidade: V1 | Estimativa: 15min | Risco: zero
Adicionar ao mypy.ini:

Bloco override para flatlib.* — ignore_missing_imports = True
Bloco override para aiofiles.* — ignore_missing_imports = True

Elimina ~9 erros sem tocar em nenhum arquivo Python.
Após executar:
Rodar mypy e reportar nova contagem
Commit: chore: mypy.ini suppress flatlib and aiofiles stubs
Registrar em completed-ag.md


BATCH 2 — IMPLICIT OPTIONAL BATCH
Velocidade: V1 | Estimativa: 30min | Risco: zero
Padrão a corrigir em todos os arquivos: arg: Tipo = None → arg: Tipo | None = None
Localizações exatas:
mcp/security.py         → argumento allowed_fields
core/provenance.py      → argumento target_node_id
mcp/protools.py         → argumento keyword + cast nos 2 Returning Any
mcp/server.py           → argumento keyword
menir_intel.py          → argumentos api_key, image_path, few_shot_examples
core/synapse.py         → variável command_bus sem anotação → dict[str, Any]
core/reconciliation.py  → variável payload sem anotação → dict[str, Any]
meta_cognition.py:169   → Sequence[str] → list[str]
meta_cognition.py:180   → Sequence[str] → list[str]
meta_cognition.py:315   → session.run(**params) → session.run(parameters=dict(params))

Após executar:
Rodar mypy e reportar nova contagem
Commit: fix: implicit Optional batch + Sequence→list + type annotations
Registrar em completed-ag.md


BATCH 3 — SDK MORTA + CONTRATOS
Velocidade: V2 | Estimativa: 45min | Aguarda decisão do Arquiteto
AG escreve no inbox.md antes de executar qualquer item deste batch.
Itens pendentes:
menir_intel.py          → remover import google.generativeai (EOL Nov/2025)
remover genai.configure() e genai.GenerativeModel()
propor substituição no _get_active_model()
core/logos.py           → Literal type incompatível nas linhas 108 e 146
core/menir_runner.py    → argumentos incompatíveis na chamada MenirOntologyManager:242
envolve menir_runner.py + meta_cognition.py — dois módulos
menir_bridge.py         → 6 métodos recebem tenant_id como parâmetro
migrar para leitura via ContextVar (princípio #1)

BATCH 4 — INVOICE SKILL RUNTIME
Velocidade: V0 | Estimativa: 2h | Luiz presente obrigatório
A extração suíça JÁ EXISTE. O bloqueio é operacional.
Bugs de runtime (invisíveis ao mypy):
Bug 1: Comentários # noqa: W293 dentro da string Cypher
Neo4j recebe como texto de query e rejeita
Bug 2: vendor_uid presente nos params mas ausente na query Cypher
Bug 3: Validação Swiss UID MOD11 ausente no schema InvoiceData
Bug 4: MENIR_INVOICE_LIVE=true não definido no .env
Sequência obrigatória:

Luiz confirma presença
AG cria VELOCITY_OVERRIDE.md com fingerprint da sessão
AG executa correções 1→3
Luiz define MENIR_INVOICE_LIVE=true no .env
Teste com fixture (nunca produção)
AG deleta VELOCITY_OVERRIDE.md após commit
menir-checkpoint INVOICE_SKILL_REAL 44


SPRINT 1A — WORKFLOW INFRA
Velocidade: V1 | Estimativa: 3-4h
Objetivo: eliminar upload manual de MENIR_STATE.md para sempre.
1A.1 — menir_git_hooks.py (script Python central)
Arquivo: scripts/menir_git_hooks.py
Ponto de entrada único para todos os hooks git.
Chamado por stubs mínimos em .git/hooks/.
Lógica do pre-commit:

Ler arquivos no git diff --cached --name-only
Verificar se algum está na ZONA_VERMELHA
Se sim: verificar se VELOCITY_OVERRIDE.md existe na raiz
Se sim: verificar se o fingerprint dentro bate com MENIR_STATE.md atual
Se não bater ou não existir: sys.exit(1) com mensagem clara:
"🔴 ALERTA GALVÂNICO: arquivo V0 detectado sem VELOCITY_OVERRIDE ativo."

Lógica do post-commit:

Copiar MENIR_STATE.md para brain local
Upload para Google Drive (se MENIR_DRIVE_FOLDER_ID definido)
Rodar health scan e gerar SESSION_BRIEF.md
Upload SESSION_BRIEF.md para Drive
Chamar log_session_to_graph.py para atualizar SessionLog no Neo4j
Se commit message começa com fix:/chore: → append em completed-ag.md
Se VELOCITY_OVERRIDE.md existir → deletar após commit bem-sucedido

Stubs mínimos (apenas chamam Python):
.git/hooks/pre-commit  → #!/usr/bin/env bash + python scripts/menir_git_hooks.py pre_commit
.git/hooks/post-commit → #!/usr/bin/env bash + python scripts/menir_git_hooks.py post_commit

1A.2 — Estrutura menir-postbox/
Criar na raiz do repo:
menir-postbox/
  inbox.md         ← AG escreve quando precisa de V2/V0
  decisions.md     ← Claude escreve autorizações
  completed-ag.md  ← AG reporta execuções V1
  todo-ag.md       ← tarefas autorizadas pendentes

Protocolo de escrita (todos os arquivos):
Append-only — nunca sobrescrever
Header obrigatório: ## [ISO TIMESTAMP] — Título
Escrita atômica: gravar em .tmp, renomear para o arquivo final

Protocolo de purga (no flip de fingerprint):
Conteúdo de todos os arquivos é arquivado como propriedade
postbox_archive no nó SessionLog do fingerprint anterior
Arquivos são zerados com header de nova sessão
Isso acontece automaticamente no post-commit quando
o fingerprint em MENIR_STATE.md muda

1A.3 — CLAUDE.md na raiz
20 linhas máximo. Contém:
Fingerprint atual
Fase e estado em uma linha
Modelo de autonomia resumido (V1/V2/V0)
Lido automaticamente pelo AG no início de toda sessão

1A.4 — menir_aliases.sh
Aliases disponíveis após source ~/menir_aliases.sh:
menir-status      → snapshot rápido do sistema
menir-brief       → gera SESSION_BRIEF + sobe para Drive
menir-sync        → sync completo pós-tarefa
menir-checkpoint  → atualiza fingerprint + commit
menir-resolve     → marca blocker resolvido no Neo4j
menir-install-hooks → instala stubs nos .git/hooks/

1A.5 — Google Drive sync
Criar pasta "Menir Sync" no Google Drive.
Exportar ID como MENIR_DRIVE_FOLDER_ID no ambiente.
gdrive CLI autenticado com conta do Luiz.

Verificação final Sprint 1A:
[ ] menir-status mostra fingerprint correto
[ ] git commit dispara pre-commit + post-commit Python
[ ] Hard Lock rejeita commit em arquivo V0 sem override
[ ] SESSION_BRIEF.md aparece no Drive automaticamente
[ ] Luiz não faz upload de nada

SPRINT 1B — HEALTH SCAN
Velocidade: V1 | Estimativa: 2h
Arquivo: scripts/menir_health_scan.py
Verifica e classifica em V1/V2/V0:
mypy count atual
SDKs mortas presentes (google-generativeai, vertexai, text-embedding-004)
Arquivos de risco modificados desde último commit
Neo4j health (nós raiz presentes, tenants ativos)
requirements.txt integridade

Gera SESSION_BRIEF.md com:
Estado atual em 5 linhas
Itens V1 que AG pode executar agora
Itens V2 aguardando Arquiteto
Itens V0 aguardando Luiz
Proposta de sessão ranqueada por impacto no runway BECO


SPRINT 1C — NEO4J SESSIONLOG
Velocidade: V1 | Estimativa: 1h
Arquivo: scripts/log_session_to_graph.py
Schema do nó (um por fingerprint de sessão):
(:SessionLog {
  fingerprint:      string — chave única
  phase:            int
  first_commit_at:  datetime — setado na primeira execução
  last_commit_at:   datetime — atualizado a cada execução
  commit_hashes:    list<string> — acumulado via MERGE
  files_modified:   list<string> — acumulado
  mypy_count:       int — último valor
  tasks_completed:  list<string>
  is_closed:        boolean — false até fingerprint mudar
  duration_minutes: int — calculado no fechamento
  postbox_archive:  string — conteúdo do postbox no fechamento
})

Lógica de fechamento de sessão:
Quando o post-commit detecta que o fingerprint em MENIR_STATE.md
mudou em relação ao SessionLog aberto mais recente:
Seta is_closed: true no nó anterior
Calcula duration_minutes = last_commit_at - first_commit_at
Arquiva conteúdo do postbox em postbox_archive
Zera os arquivos de postbox com header de nova sessão
Cria novo SessionLog com o fingerprint atual

Relações no grafo:
(:User {uid:"luiz"})-[:HAD_SESSION]->(:SessionLog)
(:Menir {uid:"MENIR_CORE"})-[:LOGGED]->(:SessionLog)
(:SessionLog)-[:HAS_BLOCKER]->(:Blocker)

CAMADA 2 — AMBIENT GRAPH INGESTION
INTERFACE: CLI PRIMEIRO, TELEGRAM DEPOIS
Decisão ratificada por Claude + AG:
Fase 1 (Sprint 2A): CLI puro
menir-capture "conheci a Sarah hoje na faculdade"
Valida o core engine de extração e desambiguação sem ruído de rede.

Fase 2 (Sprint 3C unificado): Telegram como adapter burro
O bot Telegram recebe a mensagem e chama a mesma função do CLI.
Unifica AudioSkill (Sprint 3C) e Capture (Sprint 2A) num único canal.
Zero reescrita do core — apenas um adapter HTTP fino.

SPRINT 2A — menir_capture.py (V2 — schema a validar)
AG deve propor schema completo do domínio PESSOAL no inbox.md
antes de escrever qualquer código. Arquiteto valida labels e relações.
Labels propostos: Person, Project, Institution, LifeEvent, Insight, Goal
Relações propostas: MET, COLLABORATES_WITH, STUDIES_AT, WORKS_AT,
EXPERIENCED_EVENT, HAD_INSIGHT, HAS_GOAL
Todos os nós PESSOAL: [:BELONGS_TO_TENANT]->(:Tenant {name:"PESSOAL"})
Regra fundamental: nunca mais de UMA pergunta por input.
A pergunta usa contexto do grafo — nunca é genérica.

SPRINT 2B — TrustScore (V1 — On-Read)
Decisão: calcular On-Read com propriedades pré-computadas no nó.
Sem APOC (Aura Free não inclui). APOC entra quando Aura for upgraded.
Propriedades no nó Person atualizadas a cada capture:
interactions_count
last_seen_date
contexts_count
Score calculado na leitura baseado nessas propriedades.
APOC registrado como débito técnico consciente para upgrade futuro.

CAMADA 3 — BECO REVENUE UNLOCK
SPRINT 3A — invoice_skill.py ativo
Velocidade: V0 | Estimativa: 2h (não 6h)
A extração suíça JÁ EXISTE. Ver Batch 4 para execução.
SPRINT 3B — Dashboard Fase 44
Velocidade: V2 | Desbloqueado após 3A
MVP: listagem faturas + status + total período + export Crésus.
SPRINT 3C — Telegram Adapter (unificado com Camada 2)
Velocidade: V2 | Após CLI do Sprint 2A validado
Telegram como adapter burro: recebe mensagem → chama core engine.
Mesmo adapter serve AudioSkill e Capture.

CAMADA 4 — MENIR PARA OUTROS USUÁRIOS
Bootstrap genérico: qualquer novo usuário recebe CONTABIL + PESSOAL.
Cypher idempotente via MERGE.
Luiz mantém BECO + SANTOS — sem mudança no código.

SEQUÊNCIA ABSOLUTA DE EXECUÇÃO
AGORA — V1 (AG executa sem autorização):
  [ ] Batch 1: mypy.ini — flatlib + aiofiles
  [ ] Batch 2: implicit Optional em 10 localizações
  [ ] Rodar mypy → reportar nova contagem ao Arquiteto

PRÓXIMO — V1 (Sprint 1A):
  [ ] scripts/menir_git_hooks.py (pre + post commit em Python)
  [ ] Stubs mínimos em .git/hooks/pre-commit e post-commit
  [ ] menir-postbox/ com 4 arquivos e protocolo append atômico
  [ ] CLAUDE.md na raiz
  [ ] menir_aliases.sh
  [ ] Google Drive sync configurado
  [ ] Verificação: Hard Lock rejeita arquivo V0 sem override

DEPOIS — V1 (Sprint 1B + 1C):
  [ ] scripts/menir_health_scan.py calibrado
  [ ] scripts/log_session_to_graph.py com SessionLog por fingerprint
  [ ] Primeira execução: verificar nó no Neo4j Browser
  [ ] menir-checkpoint WORKFLOW_INFRA_COMPLETE 44

V2 — Aguarda Arquiteto:
  [ ] Batch 3: SDK morta + logos + runner + bridge galvânico
      (AG propõe no inbox.md, Claude autoriza no decisions.md)
  [ ] Sprint 2A: schema PESSOAL validado antes do capture.py

V0 — Luiz presente:
  [ ] Batch 4: invoice_skill runtime + MENIR_INVOICE_LIVE=true
      (criar VELOCITY_OVERRIDE.md, executar, deletar após commit)

APÓS BECO OPERANTE:
  [ ] Sprint 3B: Dashboard Fase 44
  [ ] Sprint 2B: TrustScore On-Read
  [ ] Sprint 3C: Telegram Adapter unificado
  [ ] Camada 4: bootstrap genérico CONTABIL/PESSOAL

PROTOCOLO DE SESSÃO
Início:
AG anuncia fingerprint do MENIR_STATE.md local
Claude confirma contra o Project
Divergência → sincronizar antes de qualquer execução
AG lê inbox.md — itens pendentes de decisão?
Claude lê SESSION_BRIEF.md do Drive (após Sprint 1A: automático)

Conclusão de tarefa:
Atualizar MENIR_STATE.md com novo fingerprint
Formato: MENIR-P{fase}-{YYYYMMDD}-{TASK_SLUG}
git commit → hook dispara tudo automaticamente
Até Sprint 1A completo: Luiz re-sobe MENIR_STATE.md no Project


Versão V5.5 | Co-autoria: Claude (Arquiteto) + AG (Executor) | 06/03/2026
Incorpora: Hard Lock Galvânico, hooks Python Windows-safe,
SessionLog por fingerprint com fechamento automático,
CLI-first para Capture, TrustScore On-Read, Postbox append atômico
Fingerprint de referência: MENIR-P44-20260305-MENIR_INTEL_SEALED
