> Arquivo de Sincronização — Lido por Claude (Arquiteto) e AG (Executor) no início de TODA sessão.
> Localização canônica: raiz do repo `/Menir/MENIR_STATE.md`
> Cópia espelho: `~/.gemini/antigravity/brain/MENIR_STATE.md`

---

## 🔑 FINGERPRINT DE SESSÃO
```
MENIR-P44-20260305-MYPY_AUDIT_BASELINE
```
**Como usar:**
- AG: ao iniciar sessão, leia este arquivo e anuncie o fingerprint.
- Claude: ao receber o fingerprint do AG, confirme antes de qualquer instrução.
- Se os fingerprints divergirem → parar e sincronizar antes de trabalhar.
- Formato: `MENIR-P{fase}-{YYYYMMDD}-{LAST_TASK_SLUG}`

---

## 📍 FASE ATUAL
- **Fase:** 44
- **Etapa:** Enterprise Dashboard + Swiss-Clinical CSS Modular Shell
- **Status:** Auditoria mypy em progresso (53 erros baseline → meta: 0)
- **Última tarefa concluída:** Fase 43 Part 2 — CI/CD Exit Code 0

---

## 🚨 BLOQUEADORES ATIVOS
| ID | Arquivo | Problema | Risco |
|----|---------|---------|-------|
| B1 | `menir_intel.py` | Import `vertexai` — SDK morta | 🔴 CRASH |
| B2 | `identity.py` | ContextVar[str] com default=None | 🔴 CRASH |
| B3 | `_gemini.md` | `extra="allow"` conflita com arquitetura | 🔴 CORRUPÇÃO |
| B4 | `genesis.py:92` | Person() com args inexistentes | 🔴 CRASH |
| B5 | `cresus_exporter.py:55` | Retorna None em vez de str | 🔴 CRASH |
| B6 | `README.md` | Afirma "0 erros mypy" — FALSO | 🟠 COMPLIANCE |

---

## ✅ ESTADO DO SISTEMA
```
Tenants ativos:        BECO, SANTOS
Neo4j:                 Aura Free — conectado
Nós BECO duplicados:   VERIFICAR (suspeita de 2 nós Tenant BECO)
Frontend (Tier 2):     React + Vite + TS — Auth Bridge ativo
FastAPI:               Confirmado em requirements.txt
Embedding model:       gemini-embedding-001 (768-dim) ✅
Inference model:       gemini-2.5-flash (verificar config.py)
vertexai:              AINDA IMPORTADO — remover urgente
mypy errors:           53 em 19 arquivos (baseline: 05/03/2026)
Skills instaladas:     A CONFIRMAR pelo AG
User Node (Luiz):      NÃO CRIADO — próxima expansão
```

---

## 📋 PRÓXIMAS TAREFAS (por prioridade)
```
[ ] PRÉ-1: Verificar nó BECO duplicado no Neo4j
[ ] PRÉ-2: pip install flatlib && pip install types-aiofiles
[ ] PRÉ-3: Confirmar GEMINI_INFERENCE_MODEL = "gemini-2.5-flash" em config.py
[ ] B1: Remover imports vertexai de menir_intel.py
[ ] B2: Corrigir ContextVar em identity.py
[ ] B3: Resolver extra="allow" vs extra="forbid" (_gemini.md + schemas)
[ ] B4: Corrigir genesis.py:92 — Person() com metadata{}
[ ] B5: Corrigir cresus_exporter.py:55 — return path
[ ] BATCH: Implicit Optional em 7 arquivos (menir_bridge, provenance, etc.)
[ ] SKILL: Instalar @fastapi-pro e @auth-implementation-patterns
[ ] SKILL: Criar menir-astro-extension no brain
[ ] NEO4J: Rodar bootstrap_user_luiz.cypher (dois nós raiz)
[ ] FASE 44: Enterprise Dashboard — após mypy zerado
```

---

## 🏗️ ARQUITETURA — VERDADES IMUTÁVEIS
```
1. ContextVar é a única fonte de verdade de tenant — jamais parâmetro de função
2. extra="forbid" em schemas de ENTRADA de LLM — sempre
3. asyncio.to_thread() para todo I/O síncrono em contexto async
4. Todo nó criado DEVE ter [:BELONGS_TO_TENANT]
5. BECO = fiduciária suíça | SANTOS = pessoal/Ana Caroline
6. Confiar no repo quando contradizer documentação
7. BECO é prioridade de receita — runway limitado
```

---

## 🔄 PROTOCOLO DE ATUALIZAÇÃO
Após completar qualquer tarefa da lista acima:
1. AG atualiza a seção `PRÓXIMAS TAREFAS` (marca `[x]`)
2. AG atualiza o `FINGERPRINT` com nova data e novo `LAST_TASK_SLUG`
3. AG faz commit: `git add MENIR_STATE.md && git commit -m "state: P{fase} {TASK_SLUG}"`
4. Na próxima sessão Claude/AG: lê fingerprint → confirma → trabalha

---

*Gerado por: Claude (Arquiteto Principal) | 05/03/2026*
*Atualizado por: AG após cada tarefa concluída*
