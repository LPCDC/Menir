Menir — BootNow v5.0

Camada pseudo-OS pessoal. Foco: memória auditável, Neo4j, GitOps, rotas GPT-5 e trilha ZK.

TL;DR
- BootNow: scripts/boot_now.py inicializa estado, checkpointa e roda healthchecks.
- Graph: Neo4j (local/Aura) com schema mínimo e seeds em /graph.
- GitOps: todas as alterações passam via PR com validação automática.
- Auditoria: logs/zk_audit.jsonl registra eventos com hash e timestamp.

Estrutura
.github/workflows/ → checks de PR e CI
graph/ → cypher_init.cql, seeds, validação
scripts/ → boot_now.py, mcp_server.py, utilidades
logs/ → zk_audit.jsonl (append-only)
checkpoint.md → checkpoint canônico humano

Começo Rápido
1. Python 3.12+ e Neo4j ativo.
2. Rode graph/cypher_init.cql no banco.
3. Execute python scripts/boot_now.py
4. Confirme checkpoint.md atualizado e evento em logs/zk_audit.jsonl.

Fluxo de Desenvolvimento
Branch: release/<nome> ou feat|fix|docs|refactor|chore/<slug>
Commits prefixados: feat:, fix:, docs:, refactor:, trigger:, chore:
PR obrigatória → checks automáticos:
  - valida mensagem de commit
  - exige modificação em checkpoint.md ou logs/zk_audit.jsonl
  - bloqueia marcadores de conflito <<<< >>>>

Regras de PR
Checklist mínimo:
  [ ] Testei localmente
  [ ] Atualizei checkpoint.md ou registrei evento no logs/zk_audit.jsonl
  [ ] Mensagem de commit com prefixo correto
  [ ] Sem conflitos com main

Versionamento e Release
Tag semântica (vX.Y.Z).
v5.0.0-boot consolida BootNow v5.0 e checkpoint canônico.

Segurança
- Nunca commitar segredos. Use variáveis de ambiente ou GitHub secrets.
- Logs contêm apenas hashes, não dados sensíveis.

Licença
Definir.