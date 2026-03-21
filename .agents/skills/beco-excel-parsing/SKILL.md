---
name: parsing-beco-invoices
description: Extracts financial data from BECO's Excel invoices and ingests it into the Neo4j graph with duplicate detection. Use when the user requests processing of Nicole's monthly spreadsheets.
---

# Parsing BECO Invoices

## When to use this skill
- Quando houver novos arquivos `.xlsx` da Nicole (BECO fiduciária).
- Quando precisar extrair `invoice_number`, `client_name` e `total_amount` de faturas Excel.
- Quando for necessário injetar dados de faturamento no grafo `BECO`.

## Workflow
- [ ] Listar arquivos em `tests/fixtures/real/` ou diretório indicado.
- [ ] Executar o parsing unitário para validar colunas e valores.
- [ ] Rodar a ingestão com Duplicate Guard ativado.
- [ ] Verificar nós `(:Invoice:BECO)` ou `(:QuarantineItem:BECO)` criados.

## Instructions
### 1. Ingestão Geral
Para processar todas as faturas em `tests/fixtures/real/`:
```powershell
$env:PYTHONPATH = "."; python src/v3/scripts/ingest_real_beco_invoices.py
```

### 2. Validação de Regras
- **Data de Referência**: O parser extrai o mês/ano do nome do arquivo (ex: `01.2026`) para o campo `referential_date`.
- **Duplicate Guard**: Se um `invoice_number` colidir no mesmo mês, o script redireciona o nó para a label `QuarantineItem`.

## Resources
- **Logic**: [excel_parser.py](file:///c:/Users/Pichau/Repos/MenirVital/Menir/src/v3/skills/excel_parser.py)
- **Script**: [ingest_real_beco_invoices.py](file:///c:/Users/Pichau/Repos/MenirVital/Menir/src/v3/scripts/ingest_real_beco_invoices.py)
