# push_runbook.md
Branch canônico: release/menir-aio-v5.0-boot-local
Local: C:\\Users\\Pichau\\Repos\\MenirVital
Passos:
0) python scripts\fetch_status.py (se existir) e atualizar menir_state.json se preciso
1) git add menir_state.json lgpd_policy.md output_contracts.md push_runbook.md
   git commit -m "[auto-menir] update state"
   git push origin release/menir-aio-v5.0-boot-local
2) [CONTEXT_SRC=INTERNAL] pedir ao Grok APENAS 1 artefato no Formato A
3) salvar artefato, git add/commit/push
4) registrar linha em logs\zk_audit.jsonl com ts UTC, ação e commit
