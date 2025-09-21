# Plano de Entrega Final — MENIR (Itaú primeiro) — 2025-09-21

## Objetivo
Ingerir EML/XML/PDF (R2/CR2) em Bronze→Silver→Gold, com Garfunkel para busca e Neo4j para vínculos/consultas. Evitar “Frankenstack”.

## Artefatos deste pacote
- menir.config.json (presets auto-ON)
- schemas/{documento.json, transacao.json, email.json, garfunkel_record.json}
- cypher/{config_menir.cypher, upsert_documento.cypher, upsert_transacao.cypher, thread_email.cypher, sanity_reports.cypher, cleanup.cypher}
- templates/{records.jsonl, log_versoes_modelo.csv}
- docs/{MODEL.md, INGEST.md, CHECKPOINT.md} (este plano)
- pipeline/README.md

## Perguntas fundamentais (20) — responder para fechar especificação
1) Onde ficam Bronze/Silver/Gold (URI)?
2) Limites de tamanho e tempo de OCR?
3) Versão/stack de R2/CR2 (idiomas)?
4) OCR sempre ligado ou fallback?
5) Limiar de quarentena (ex.: <0.70)?
6) Critério de merge near-dup (prioridade)?
7) Campos PII proibidos no Gold?
8) Retenção/TTL para Bronze e Silver?
9) Lista final de doc_type?
10) Política de versão vNN e log central?
11) Garfunkel: campos obrigatórios JSONL?
12) Canal de alertas (e-mail/Telegram)?
13) LGPD: base legal por projeto?
14) Portas de entrada: manual, GitHub, IMAP/Drive?
15) Naming e timezone confirmados?
16) CET: planilha obrigatória? formato?
17) Campos financeiros mínimos?
18) E-mail: cabeçalhos obrigatórios e charset?
19) Política de auditoria/approvals (JSON)?
20) Projetos na primeira onda e prioridades?

## Próximas tasks (20) — execução
1) Criar menir.config e gravar Config no Neo4j.
2) Parser EML (headers+anexos) → Silver JSONL.
3) Threading por Message-ID/In-Reply-To.
4) Parser XML camt.053 (OFX fallback) → Transacao.csv.
5) R2/CR2 PDF (OCR+depuração+interpretação) → Silver.
6) Normalizadores (datas/moedas/%/citações).
7) Dedupe (sha256 + tlsh/ssdeep) + quarentena.
8) Export Silver→Garfunkel (records.jsonl).
9) Upsert Documento + REFERE_A.
10) Upsert Transacao + ENVOLVENDO.
11) ANEXA (email→anexo) e REPLY_TO (email thread).
12) Relatórios de sanidade.
13) CET validator + exigência de planilha.
14) Alertas (CET=0%, incoerências).
15) PII redaction em prévias.
16) Version log CSV + diff entre versões.
17) MODEL.md e INGEST.md concluídos.
18) Script de limpeza mensal.
19) Checklist jurídico aplicado à minuta.
20) Ofício parametrizado p/ envio (se necessário).

## Critérios de aceite
- Pipeline processa EML/XML/PDF caóticos em Bronze→Silver→Gold sem erro.
- Garfunkel indexa `records.jsonl`; Neo4j tem nós/rel vínculos.
- Relatórios de sanidade executam e retornam 0 críticos após limpeza.
- CET validator exige planilha; ofício gerado sob demanda.
