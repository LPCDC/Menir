# INGEST.md (MENIR — Bronze → Silver → Gold)

## Fluxo
1) **Bronze**: guardar bruto (EML, XML camt.053/OFX, PDF).
2) **Silver**: extrair metadados + conteúdo (JSONL/CSV).
   - **PDF via R2/CR2**: OCR → depuração → interpretação → JSONL
   - **EML**: cabeçalhos RFC 5322, anexos separados, threading por Message-ID.
   - **XML camt.053** (OFX fallback): mapear Transacao (EndToEndId/FITID).
3) **Gold (Neo4j)**: só índices e vínculos (sem payload).

## Dedupe
- Exato: sha256
- Aproximado: tlsh/ssdeep
- Quarentena < 0.70 de confiança

## Saída para Garfunkel
- `templates/records.jsonl` (exemplo)
- Campos: record_id, doc_type, text, fields, tables, links, hashes, project_slug

## Validações
- Relatórios de sanidade (cypher/sanity_reports.cypher)
- CET validator: exige planilha e consistência
