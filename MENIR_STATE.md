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

---

## ✅ CONCLUÍDO (Momento 1 - Fase 47)
- [x] Neo4j AsyncDriver Migration (Complete)
- [x] MenirBridge Async Conversion (Complete)
- [x] Priority Gateway & Latency Benchmark (Complete)
- [x] ImportBatch Canonical Cypher (Complete)
- [x] Security: Strict 401 Auth (Complete)
- [x] PDF Memory Semaphore & Cleanup (Complete)

---

## 🏗️ VERDADES IMUTÁVEIS
1. ContextVar é única fonte de verdade de tenant — jamais parâmetro de função
2. **NOVO:** Proibido `session.run()` direto em fluxos financeiros (Use execute_write).
3. **NOVO:** Proibido `shutil.move()` para arquivamento Synology (Use FastArchiveWorker).
4. asyncio.to_thread() para todo I/O síncrono em contexto async.
5. BECO é prioridade de receita — SANTOS é domínio pessoal.

*Gerado por: AG (Executor) | 21/03/2026*
