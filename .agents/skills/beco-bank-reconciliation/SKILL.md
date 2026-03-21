---
name: reconciling-beco-bank
description: Ingests CAMT053 statements and reconciles bank credits with invoices for the BECO tenant. Use when handling BCGE bank statements or payment matching.
---

# Reconciling BECO Bank Statements

## When to use this skill
- Recebimento de arquivos `CAMT.053` da BCGE.
- Necessidade de marcar faturas como `PAID` automaticamente.
- Verificação de discrepâncias entre valores faturados e recebidos.

## Workflow
- [ ] Injetar transações do banco no grafo.
- [ ] Rodar o motor de reconciliação fuzzy.
- [ ] Revisar discrepâncias (ex: 575 CHF faturados vs 500 CHF pagos).
- [ ] Validar arestas `[:RECONCILED]` entre `Transaction` e `Invoice`.

## Instructions
### 1. Ingestão de Extrato (CAMT053)
```powershell
$env:PYTHONPATH = "."; python src/v3/scripts/ingest_real_beco_camt.py
```

### 2. Execução da Reconciliação
```powershell
$env:PYTHONPATH = "."; python src/v3/scripts/reconcile_beco.py
```

### 3. Regras de Match
- **Fuzzy Name**: Compara `c.name` (Client) com `tr.debtor_name` (Transaction) usando `toLower` e `CONTAINS`.
- **Tolerância**: Aceita discrepâncias de até 100 CHF por padrão (ajustável no script).

## Resources
- **Ingest Script**: [ingest_real_beco_camt.py](file:///c:/Users/Pichau/Repos/MenirVital/Menir/src/v3/scripts/ingest_real_beco_camt.py)
- **Reconcile Script**: [reconcile_beco.py](file:///c:/Users/Pichau/Repos/MenirVital/Menir/src/v3/scripts/reconcile_beco.py)
- **Skill Core**: [camt053_skill.py](file:///c:/Users/Pichau/Repos/MenirVital/Menir/src/v3/skills/camt053_skill.py)
