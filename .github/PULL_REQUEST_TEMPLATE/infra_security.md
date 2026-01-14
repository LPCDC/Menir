---
name: Infra / Security / Hardening
about: Template rigoroso para mudanças em backup, auth, logs ou infraestrutura.
title: "infra: [Mudança Crítica]"
labels: ["security", "infrastructure"]
assignees: []
---

## 🛡️ Escopo Crítico
*(Mudanças em Data, Logs, Auth ou Backup exigem revisão dupla.)*

- **Componente**: (Ex: Backup Routine, MCP Auth, Dockerfile)
- **Impacto**: (Ex: Altera formato de log, requer novo .env)

## 🔒 Checklist de Segurança (Obrigatório)
- [ ] **Persistência**: Garantiu que nenhum dado está sendo deletado sem backup prévio?
- [ ] **Segredos**: Verificou se NÃO há chaves/tokens hardcoded no código?
- [ ] **Observabilidade**: A mudança gera logs estruturados (JSONL) para sucesso/falha?
- [ ] **Revert**: Existe plano de rollback se isso quebrar em produção?

## 🧪 Validação de Infra
- [ ] **Smoke Test**: Rodou `scripts/verify_release.py`? Resultado?
- [ ] **Disaster Recovery**: Validou se o backup/restore continua funcionando?

## ⚠️ Breaking Changes
- [ ] Requer atualização de `.env`?
- [ ] Requer migração de dados (Schema)?

---
*Menir Hardening Policy — Trust but Verify.* 🛡️
