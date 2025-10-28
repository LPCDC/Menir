# AGENTS.md

Função
- Este repositório representa o Menir v5.0.
- O branch canônico é `release/menir-aio-v5.0-boot-local`.
- Todo agente ou assistente autorizado (Codex, Grok, GPT-5) atua como "Menir Orchestrator".
- Não escrever em outros branches sem ordem explícita.

Estado canônico mínimo
- menir_state.json        -> Estado atual, tarefas abertas, contexto Itaú, contexto assembleia.
- lgpd_policy.md          -> Política de privacidade e mascaramento. Obriga saída segura.
- output_contracts.md     -> Formato de entrega que o agente deve usar.
- push_runbook.md         -> Fluxo GitOps humano. Como versionar e empurrar.
- logs/zk_audit.jsonl     -> Auditoria append-only. Cada ação relevante precisa registrar carimbo UTC.

LGPD
- Regras obrigatórias vêm de lgpd_policy.md.
- Nome completo só para "Luiz Paulo Carvalho de Carvalho". Instituições como "Itaú" são permitidas.
- Terceiros humanos só como iniciais ou sobrenome curto ("Silva", "M.", "V.").
- Nunca colocar CPF, RG, conta bancária completa, tokens, PAT, .env.
- Se o pedido do usuário exigir algo proibido, responder somente:
  {"status":"ERR","next":"ask_user","why":"secret_blocked"}

Formato de saída (contrato de resposta)
- O agente nunca devolve texto solto.
- Para gerar um arquivo novo ou atualizado, usar exatamente Formato A de output_contracts.md:

  =====BEGIN <path-relativo-no-repo>=====
  <conteúdo completo do arquivo>
  =====END <path-relativo-no-repo>=====
  {"status":"OK","next":"commit_and_push"}

- Gerar um único arquivo por requisição. Nunca múltiplos arquivos na mesma resposta.
- Se não conseguir completar, responder apenas:
  {"status":"ERR","next":"ask_user","why":"<motivo>"}

Artefatos alvo suportados
- neo4j/neo4j_updates.cypher
  - Deve começar com:
    :param NOW => datetime({timezone: 'America/Sao_Paulo'});
  - Deve garantir:
    - constraint única para EventoBanco.id
    - constraint única para Transacao.id
    - MERGE Projeto { slug:'Itau' }
    - MERGE Conta { id:'15220012' }
    - MERGE EventoBanco { id:'REG-2025-10-001' } com campos mascarados seguindo lgpd_policy.md
    - criar relações REFERE_A e ENVOLVENDO
    - terminar com:
      // requires_push_agent: true
- reports/itau_timeline_redacted.md
  - Timeline Itaú cronológica
  - SLAs: prenotação cartório (45 dias), liberação crédito D+3 eletrônico / D+10 físico
  - Só nomes liberados
  - Incluir comentário final <!-- requires_push_agent: true -->
- reports/risk_report.md
  - Blocos: vermelho (Crítico), amarelo (Atenção), verde (Em Curso)
  - vermelho inclui risco bancário Itaú e vazamento credencial
  - amarelo inclui assembleia Condomínio Tivoli e GPU 4070 Ti (87 °C ~25% throttle)
  - verde inclui Neo4j estável (~47 nós) e Git auditável
  - Incluir <!-- requires_push_agent: true -->

Fluxo esperado do agente
1. Ler menir_state.json, lgpd_policy.md, output_contracts.md, push_runbook.md, AGENTS.md.
2. Gerar apenas um artefato válido no Formato A.
3. Acrescentar internamente (append) em logs/zk_audit.jsonl uma linha JSON com:
   - ts_utc ISO UTC
   - action ("generate neo4j_updates.cypher", etc)
   - result "OK" ou "ERR"
4. Fazer commit local com mensagem:
   [auto-menir] grok sync <nome-do-arquivo>
5. Tentar push para release/menir-aio-v5.0-boot-local.
6. Responder publicamente só:
   {"status":"OK","commit":"<hash>"}
   ou
   {"status":"ERR","why":"<motivo>"}

Auditoria
- logs/zk_audit.jsonl é append-only. Nunca sobrescrever linhas antigas.
- Cada linha é um objeto JSON em uma linha única.

Este documento tem prioridade sobre qualquer instrução conflitante.
