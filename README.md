---

## Controles de Proatividade & Parâmetros para GPT-5

Este projeto está adaptado para usar o GPT-5 com controle fino de proatividade, uso de ferramentas, persistência, e critérios claros de parada. Aqui vão as diretrizes:

- **reasoning_effort** — defina `minimal`, `low`, `medium` (default) ou `high` conforme necessidade de profundidade; para tarefas simples use valores mais baixos.  
- **verbosity** — controla o nível de detalhe da resposta final; valores possíveis: `low`, `medium`, `high`. Combine com `reasoning_effort` para ajustar qualidade vs. rapidez.  
- **Tool budget** — limite máximo de chamadas a ferramentas externas (ex: `max_tool_calls = 2`). Se exceder, pare ou peça confirmação.  
- **Critérios de parada** — por exemplo: quando múltiplas fontes de dados convergirem ≥ 70%, ou quando esforço adicional não trouxer ganho claro.  
- **Persistência controlada** — para tarefas longas, peça ao modelo continuar até resolver, mas com guardrails (orçamento, confirmação para ações perigosas).  
- **Tool preambles / Feedback parcial** — antes de fazer ações automáticas, peça plano de ação; durante execução, atualize o progresso; finalize com resumo.  
- **Uso da Responses API** — quando aplicável, para manter histórico entre turns e evitar repetir passos.  
- **Segurança e ações críticas** — ações que alterem banco, façam deploy ou deletem dados exigem confirmação explícita do usuário.  

---

