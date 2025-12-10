# Roadmap de Pesquisa Menir v1.2+ (Autonomous Agentic OS)

**Data**: 10/12/2025
**Meta**: Evoluir de "Personal OS" (Registro Passivo) para "Autonomous Agentic OS" (Agente Ativo).

---

## 🔬 1. Eixos de Pesquisa (Benchmark & Strategy)

### 1.1. Graph RAG (Knowledge-Graph + LLM)
**Conceito**: Recuperação de informação baseada em estruturas de grafo (relacionamentos) e não apenas similaridade vetorial.
*   **Referência**: "Graph RAG demo based on Jaguar data and GPT-4".
*   **Aplicação no Menir**:
    *   *Query*: "Qual foi o impacto das sessões da semana passada no projeto Débora?"
    *   *Mecanismo*: LLM gera Cypher query -> Menir executa no Neo4j -> LLM sintetiza resposta com contexto do grafo.
*   **Dependências**: Ontologia robusta (`narrative.ttl`), Graph Database populado (via Scribe).
*   **Risco**: Alucinação na geração de Cypher.
*   **Mitigação**: Camada de validação de schema antes da execução da query; Ferramentas de "Query Dry Run".

### 1.2. Self-Evolving Agents (Auto-Evolução)
**Conceito**: Agentes que refinam seu próprio comportamento baseados em feedback e métricas de sucesso.
*   **Referência**: "Self-Evolving Agents – A Cookbook for Autonomous Agent Retraining" (OpenAI).
*   **Aplicação no Menir**:
    *   *Loop*: O "Scribe" gera uma proposta de grafo -> Usuário corrige (reject/edit) -> Scribe analisa o diff e atualiza seu "System Prompt" ou "Few-Shot Examples" para a próxima vez.
*   **Riscos**: Degradação de performance (overfitting em correções recentes).
*   **Mitigação**: Versionamento de prompts do agente; "Golden Set" de testes de regressão antes de auto-atualizar.

### 1.3. Arquiteturas Híbridas (Soberania vs Inteligência)
**Conceito**: Uso de IA em nuvem (Cérebro Efêmero) com persistência local (Memória Eterna).
*   **Estratégia**:
    *   **Dados Quentes** (Contexto Imediato): Memória RAM/Cache do Agente.
    *   **Dados Mornos** (Sessão Atual): Arquivos locais temporários.
    *   **Dados Frios** (Histórico): Grafo AuraDB + Logs JSONL (Backup Local).
*   **Privacidade**: O agente roda local (MCP), envia apenas o *contexto necessário* para a API da LLM, nunca o dump completo do banco.

---

## 🏗️ 2. Plano de Execução Técnica (Sprint v1.2)

### 2.1. Consolidação da Infra (Ponte v1.1 -> v1.2)
*   **Tarefa 1**: `menir_cli.py` (Unified CLI).
    *   Substituir scripts isolados por uma interface coesa (`menir start`, `menir status`).
    *   *Justificativa*: Reduz carga cognitiva e prepara terreno para comandos complexos de agente.

### 2.2. The Scribe (Motor de Ingestão)
*   **Tarefa 2**: Implementar Engine de Leitura (`data/debora/*.txt`).
*   **Tarefa 3**: Implementar "Proposal System" (Diff JSON).
    *   *Regra*: O agente nunca escreve no Grafo diretamente. Ele propõe mudanças, o sistema (ou usuário) aplica. Isso garante a segurança dos dados durante a fase de "Self-Evolution".

### 2.3. Prova de Conceito (PoC) GraphRAG
*   **Tarefa 4**: Script `query_graph_context.py`.
    *   Recebe pergunta em NL -> Traduz para busca híbrida (Vector + Graph) -> Responde.

---

## ⚠️ 3. Avaliação de Riscos (Risk Assessment)

| Risco | Probabilidade | Impacto | Plano de Contigência |
| :--- | :--- | :--- | :--- |
| **Custo de API (LLM)** | Alta | Médio | Cache agressivo de queries; Usar modelos menores (Haiku/GPT-4o-mini) para tarefas rotineiras. |
| **Corrupção do Grafo** | Média | Alto | Backup (Zip) antes de qualquer batch write; Scribe Proposal System (Human-in-the-loop). |
| **Complexidade de Setup** | Alta | Médio | Manter `menir_cli.py` com comando `menir doctor` para auto-diagnóstico. |

---
*Aprovado como base para o desenvolvimento da v1.2.*
