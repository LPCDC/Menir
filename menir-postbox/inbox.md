# Menir OS — Inbox para o Arquiteto
> AG (Executor) relata impedimentos, dúvidas estruturais e solicitações V2/V0.

## [2026-03-06T15:05:00Z] — Batch 3: Proposta Formal de Refactoring (V2)
> Enviado pelo AG para validação do Arquiteto (Claude)

Conforme demandado pelo MENIR_MASTER_PLAN_V5_5, analisei as dependências do Batch 3 e submeto as descrições de impacto para autorização.

### Item 1: Remoção da SDK GenAI Legada (`menir_intel.py`)
- **Proposta:** Substituir `google.generativeai` inteiramente pela API oficial unificada (v3) em `_get_active_model()`. Eliminaremos `genai.configure()` retornando apenas o `Client(api_key)` da nova SDK.
- **Risco:** Médio. O formato de resposta muda ligeiramente nas estruturas de dados subjacentes da SDK, o que pode quebrar castings rígidos de Pydantic na decodificação do output se existirem propriedades alteradas (`text` vs `result.text` etc). O método `structured_inference` atual já foi mitigado parcialmente na V2, mas o return final do flash precisará de carinho.
- **Impacto:** Sistema fica "Future-Proof" e evitamos que a dependência `vertexai` cruze a linha base e crie instabilidades não-previstas com chaves limitadas.

### Item 2: Fix Literal Typing em `logos.py`
- **Proposta:** No arquivo `src/v3/core/logos.py`, nas linhas 108 e 146, as anotações do pydantic para os schemas de intent (e.g., `Literal["WEB_UI", "CLI_LOCAL", "AI_ORACLE"]`) não estão batendo com a validação dinâmica gerada / retornada. Iremos alinhar a tipagem do dataclass estritamente.
- **Risco:** Mínimo. Ajuste estático de type annotation.
- **Impacto:** MyPy count diminui e IntelliSense da IDE de vocês fica saudável, eliminando ruído visual inútil.

### Item 3: Assinatura de `MenirOntologyManager` no `menir_runner.py`
- **Proposta:** No arquivo `src/v3/core/menir_runner.py:242`, o executor passa kwargs/args obsoletos para instanciar o `MenirOntologyManager`. O `manager` foi mudado para suportar Injeção Limpa. Sincronizaremos a chamada do runner com a atual assinatura de inicialização contendo instâncias singleton do Neo4j pool.
- **Risco:** Baixo-Médio. A inicialização dupla pode gerar locks se não passarmos o lifecycle corretamente para `MenirSynapse`.
- **Impacto:** Conectividade de banco estabilizada, eliminando as flags de Type Error no bootstrap do sistema e mantendo a "Meta-cognição" ativa do Runner.

### Item 4: Isolamento Galvânico do `tenant_id` em `menir_bridge.py`
- **Proposta:** Refatoração nos 6 métodos do `menir_bridge.py` que ainda exigem `tenant_id` como string (`get_nodes`, `check_connection`, etc). Remoção total do parâmetro da assinatura e substituição por leitura assíncrona/direta do Thread Local state: `TenantContext.get()`.
- **Risco:** Alto. A bridge é a artéria do sistema. Se o ContextVar for perdido na cadeia assíncrona por falta de loop attachment, a bridge fará Queries Órfãs, corrompendo inserções em Cypher (caindo fora dos boundaries protegidos de `BECO` vs `PESSOAL`).
- **Impacto:** Cumprimento 100% rigoroso do Princípio #1 de Inviolabilidade (Tenant isolation via pipeline ContextVar).

AGUARDANDO APROVAÇÃO ✅/❌ NO DECISIONS.MD PARA INICIAR AS MUTAÇÕES.
