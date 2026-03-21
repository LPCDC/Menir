> Arquivo de Sincronização — Lido por Claude (Arquiteto) e AG (Executor) no início de TODA sessão.
> Localização canônica: raiz do repo `/Menir/MENIR_STATE.md`
Cópia espelho: `~/.gemini/antigravity/brain/MENIR_STATE.md`

---

## 🔑 FINGERPRINT DE SESSÃO
```
MENIR-P47-20260321-HARDENING-SEMGREP-ISOLATION
```
- AG: anuncie este fingerprint ao iniciar sessão.
- Claude: confirme antes de qualquer instrução.
- Divergência → parar e sincronizar antes de trabalhar.
- Formato: `MENIR-P{fase}-{YYYYMMDD}-{LAST_TASK_SLUG}`

---

## 📍 FASE ATUAL
- **Fase:** 47
- **Etapa:** Closing Momento 1 (Hardening & Isolation)
- **Status:** Regras Semgrep de conformidade Fase 48 implementadas. Auditoria de isolamento de drivers concluída.
- **Resultados da Sprint:**
  - Semgrep: `prohibit-direct-session-run-finance` + `prohibit-shutil-move-cross-fs` ativos em `.semgrep/menir_v3_rules.yaml`.
  - Auditoria: Detectado uso de `Driver` síncrono em handlers assíncronos do Synapse (Risco de Deadlock).
  - Momento 1: SELADO com fingerprint definitivo P47-M1-GOLDEN-MASTER-SEALED.

---

### Status Atual (Sessão Atual)
- [x] **Fase 47 - Etapa 5**: ImportBatch & unique constraint `Client.client_id`.
- [x] **Fase 47 - Etapa 6**: Priority Gateway (SANTOS < 200ms) implementado e validado (15ms).
- [x] **Hardening Final**: Regras Semgrep para `session.run()` e `shutil.move()` (Pre-Fase 48).
- [x] **Auditoria**: Mapeamento de Deadlock Risk entre Synapse e OntologyManager.
- [ ] **MOMENTO 2 (PENDENTE)**: Iniciar Etapa 7 - Menir Companion Tauri.

---

## 🚨 DÍVIDA TÉCNICA (ZONA VERMELHA)
- **ID-47-01**: Risco de Deadlock no `synapse.py`. O `handle_get_quarantine_documents` consome o pool síncrono do `OntologyManager` em contexto async saturado. Mitigar como Tarefa 1 do Momento 2.

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
17. **NOVO:** Proibido `session.run()` direto em fluxos financeiros (Use execute_write).
18. **NOVO:** Proibido `shutil.move()` para arquivamento Synology (Use FastArchiveWorker).

*Gerado por: AG (Executor) | 21/03/2026*
