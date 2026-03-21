---
name: reporting-beco-finance
description: Generates financial summary reports for the BECO tenant. Use when calculating total faturamento, unpaid items, or monthly P&L.
---

# Reporting BECO Finance

## When to use this skill
- Fechamento mensal de faturamento.
- Necessidade de lista de devedores (`unpaid invoices`).
- Solicitação de métricas de performance financeira ("Quanto faturamos em Janeiro?").

## Workflow
- [ ] Garantir que invoices e transações do período foram ingeridas.
- [ ] Executar o gerador de relatório.
- [ ] Analisar o JSON gerado (`beco_january_2026_report.json`).

## Instructions
### 1. Gerar Relatório Consolidado
```powershell
$env:PYTHONPATH = "."; python src/v3/scripts/generate_beco_report.py
```

### 2. Métricas Extraídas
- **Total Billed**: Soma de `total_amount` de todas as faturas no período.
- **Paid vs Unpaid**: Contagem baseada na existência da aresta `[:RECONCILED]`.
- **Quarantine Check**: Lista faturas bloqueadas por colisão ou erro.

## Resources
- **Generator**: [generate_beco_report.py](file:///c:/Users/Pichau/Repos/MenirVital/Menir/src/v3/scripts/generate_beco_report.py)
