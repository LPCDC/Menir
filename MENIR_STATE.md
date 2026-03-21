> Arquivo de Sincronização — Lido por Claude (Arquiteto) e AG (Executor) no início de TODA sessão.
> Localização canônica: raiz do repo `/Menir/MENIR_STATE.md`
Cópia espelho: `~/.gemini/antigravity/brain/MENIR_STATE.md`

---

## 🔑 FINGERPRINT DE SESSÃO
```
MENIR-P47-20260321-TAURI-MVP-SSE
```
- AG: anuncie este fingerprint ao iniciar sessão.
- Claude: confirme antes de qualquer instrução.
- Divergência → parar e sincronizar antes de trabalhar.
- Formato: `MENIR-P{fase}-{YYYYMMDD}-{LAST_TASK_SLUG}`

---

## 📍 FASE ATUAL
- **Fase:** 47
- **Etapa:** Momento 2 - Etapa 7 Concluída
- **Status:** Menir Companion Tauri MVP funcional com SSE e REST POST sob isolamento galvânico.
- **Resultados da Sprint:**
  - Boilerplate Tauri: Inicializado e configurado para Windows (Texto Puro).
  - Synapse: Endpoints `/api/v3/events/companion` (SSE) e `/api/v3/companion/command` (REST) ativos.
  - TDD: Testes de SSE e Comandos validados (auth rejection e stream open).
  - Isolamento: Tenant extraído incondicionalmente via JWT.

---

### Status Atual (Sessão Atual)
- [x] **Fase 47 - Etapa 5**: ImportBatch & unique constraint `Client.client_id`.
- [x] **Fase 47 - Etapa 6**: Priority Gateway (SANTOS < 200ms) implementado e validado (15ms).
- [x] **Hotfix ID-47-01**: Deadlocked resolved in `synapse.py`.
- [x] **Fase 47 - Etapa 7**: Menir Companion Tauri MVP (SSE + REST).
- [ ] **MOMENTO 2 (PENDENTE)**: Iniciar Etapa 8 - BillingRule.

---

## 🚨 DÍVIDA TÉCNICA (ZONA VERMELHA)
- **ID-47-02**: EventSource sem suporte nativo a Headers. Implementar `short-lived token exchange` (POST `/api/v3/auth/sse-token`) para produção.

---

## 🏗️ VERDADES IMUTÁVEIS

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
13. AG is reactive, not a daemon — it runs when called, not in the background.
14. Velocidade 1: AG notifica depois. Velocidade 2: AG propõe antes.
15. Hooks sempre em Python — nunca Bash puro no Windows
16. Postbox é append-only — nunca sobrescrever, purgar para Neo4j no flip de fingerprint
17. Proibido session.run() direto em fluxos financeiros (Use execute_write).
18. Proibido shutil.move() para arquivamento Synology (Use FastArchiveWorker).

---

*Gerado por: AG (Executor) | 21/03/2026*
