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
- Para gerar um arquivo novo ou atualizado, usar exatamente o Formato A de output_contracts.md:

=====BEGIN <path-relativo-no-repo>=====
<conteúdo completo do arquivo>
=====END <path-relativo-no-repo>=====
{"status":"OK","next":"commit_and_push"}

- Gerar um único arquivo por requisição. Nunca múltiplos arquivos.
- Se não conseguir completar, responder apenas:
  {"status":"ERR","next":"ask_user","why":"<motivo>"}

Artefatos alvo suportados
- neo4j/neo4j_updates.cypher
  - Primeira linha:
    :param NOW => datetime({timezone: 'America/Sao_Paulo'});
  - Garantir:
    - constraint única EventoBanco.id
    - constraint única Transacao.id
    - MERGE Projeto { slug:'Itau' }
    - MERGE Conta { id:'15220012' }
    - MERGE EventoBanco { id:'REG-2025-10-001' } com campos mascarados conforme lgpd_policy.md
    - relações REFERE_A e ENVOLVENDO
    - última linha: // requires_push_agent: true
- reports/itau_timeline_redacted.md
  - Timeline cronológica Itaú, SLAs (45 dias registro; D+3/D+10 liberação), nomes conforme política
  - Incluir: <!-- requires_push_agent: true -->
- reports/risk_report.md
  - Blocos: vermelho (Crítico), amarelo (Atenção), verde (Em Curso)
  - Incluir riscos Itaú, credenciais, assembleia Tivoli/Iberê, GPU 4070 Ti
  - Incluir: <!-- requires_push_agent: true -->

Fluxo esperado do agente
1. Ler menir_state.json, lgpd_policy.md, output_contracts.md, push_runbook.md, AGENTS.md.
2. Gerar apenas um artefato válido no Formato A.
3. Acrescentar linha em logs/zk_audit.jsonl (ts_utc ISO, action, result).
4. Commit local: [auto-menir] grok sync <nome-do-arquivo>
5. Push para release/menir-aio-v5.0-boot-local.
6. Resposta pública final:
   {"status":"OK","commit":"<hash>"}
   ou
   {"status":"ERR","why":"<motivo>"}

Auditoria
- logs/zk_audit.jsonl é append-only; uma linha JSON por evento.
