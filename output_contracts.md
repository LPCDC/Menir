# output_contracts.md
Formato A:
=====BEGIN <path>=====
<conteúdo>
=====END <path>=====
{"status":"OK","next":"commit_and_push"}

Formato B (falha):
{"status":"ERR","next":"ask_user","why":"<motivo>"}

Artefatos válidos:
1) neo4j/neo4j_updates.cypher
   - primeira linha: :param NOW => datetime({timezone: 'America/Sao_Paulo'});
   - constraints únicas: EventoBanco.id, Transacao.id
   - MERGE Projeto{slug:'Itau'}, Conta{id:'15220012'}
   - MERGE EventoBanco{id:'REG-2025-10-001'} com campos mascarados
   - relações REFERE_A e ENVOLVENDO
   - última linha: // requires_push_agent: true
2) reports/itau_timeline_redacted.md (cronologia + SLAs; terceiros mascarados; <!-- requires_push_agent: true -->)
3) reports/risk_report.md (vermelho/amarelo/verde; <!-- requires_push_agent: true -->)
