# 🛑 Menir — Daily Check-Out Ritual

## Purpose

Ritual de encerramento **seguro** antes de sair do Codespace ou encerrar a sessão, garantindo que:
- Repositório está sincronizado (pull)
- Grafo e schema estão íntegros (health check)
- Todos dados foram salvos e pushados (git commit/push)
- Checkpoint foi criado para auditoria

---

## Two Options

### Option 1: Bash Script (Recommended)

```bash
./menir_daily_checkout.sh
```

**O que faz:**
1. Pull origin/main
2. Roda health check completo
3. Mostra relatório
4. Git add/commit/push
5. Oferece criar tag checkpoint (opcional)

**Saída:**
```
╔════════════════════════════════════════════════════════════════╗
║           Menir Daily Check-Out Ritual                         ║
╚════════════════════════════════════════════════════════════════╝

[1/6] Pulling latest changes from main...
✅ Pull completed

[2/6] Running full health check...
Menir Full Check Report — ...
✅ Schema OK
📊 Contagens principais: ...
✅ FULL CHECK PASSED

[3/6] Health check report:
...

[4/6] Current git status:
(working tree clean)

[5/6] Committing and pushing...
ℹ️  No changes to commit (working tree clean)

[6/6] Optional: Create checkpoint tag?
  Create checkpoint tag now? (y/N): 
```

---

### Option 2: Python Script

```bash
python3 menir_daily_checkout.py
```

Mesmas funcionalidades que a versão bash, com input interativo para checkpoint tag.

---

## Automated Checkpoint

Para **criar tag automaticamente** (sem prompt), use flag:

```bash
# Bash: edit script ou rode manualmente
git tag -a "checkpoint-$(date +%Y%m%d)" -m "Checkpoint $(date)"
git push origin $(git tag -l | tail -1)

# Python: será adicionado em próxima versão
```

---

## Typical Workflow at End of Day

```bash
# ... finish work ...

# 1. Run checkout ritual
./menir_daily_checkout.sh

# 2. Answer checkpoint prompt (y/N)
#    → Creates checkpoint-YYYYMMDD tag automatically

# 3. Verify all green (✅ OK)

# 4. Safe to close Codespace / shutdown
exit
```

---

## What Gets Saved

| Component | Action |
|-----------|--------|
| **Health Reports** | Updated + committed |
| **Code Changes** | Committed to main |
| **Git History** | Pushed to origin |
| **Checkpoint Tag** | Created if requested |
| **Git Status** | Verified clean |

---

## Example Output

```
╔════════════════════════════════════════════════════════════════╗
║           Menir Daily Check-Out Ritual                         ║
║           2025-12-06 23:10:00 UTC                              ║
╚════════════════════════════════════════════════════════════════╝

[1/6] Pulling latest changes from main...
✅ Pull completed

[2/6] Running full health check...
Menir Full Check Report — 2025-12-06T23:10:15.123456
✅ Schema OK
📊 Contagens principais: {'Work': 2, 'Chapter': 2, 'Character': 9, 'Scene': 4, 'Event': 13}
✅ Todas cenas têm eventos
✅ FULL CHECK PASSED

[3/6] Health check report (first 15 lines):
---
{
  "timestamp": "2025-12-06T23:10:15.123456",
  "neo4j_uri": "bolt://localhost:7687",
  "schema": {
    "missing_labels": [],
    "extra_labels": []
  },
  "counts": {
    "Work": 2,
    "Chapter": 2,
    "Character": 9,
    "Scene": 4,
    "Event": 13
  },
...

[4/6] Current git status:
ℹ️  Working tree clean

[5/6] Committing and pushing...
ℹ️  No changes to commit (working tree clean)

[6/6] Optional: Create checkpoint tag?
  Command: git tag -a 'checkpoint-20251206' -m 'Checkpoint 2025-12-06 23:10:00 UTC'

  Create checkpoint tag now? (y/N): y
✅ Tag 'checkpoint-20251206' created and pushed

╔════════════════════════════════════════════════════════════════╗
║                   ✅ Check-Out Complete                        ║
║                                                                ║"
║  Repository is clean and synced. Safe to close Codespace.    ║
╚════════════════════════════════════════════════════════════════╝
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Push rejected" | Manually merge, resolve conflicts, retry |
| "Health check failed" | Review report, fix issues, re-run script |
| "Tag already exists" | Use different suffix or manual tagging |
| "No changes to commit" | Perfectly fine — repo is clean |

---

## Integration with CI/CD

Para **automação em GitHub Actions**, use non-interactive version:

```bash
#!/bin/bash
python3 scripts/health_check_full.py
git add .
git commit -m "chore: nightly health check" || true
git push origin main
git tag -a "nightly-$(date +%Y%m%d)" -m "Nightly checkpoint"
git push origin "nightly-$(date +%Y%m%d)" || true
```

---

## Next: Automate via Cron

Para rodar **diariamente às 23:00**, adicione a `.github/workflows/` ou crontab local:

```yaml
name: Daily Checkout

on:
  schedule:
    - cron: '0 23 * * *'  # 23:00 UTC daily

jobs:
  checkout:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: bash menir_daily_checkout.sh
```
