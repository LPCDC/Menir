# Menir – GraphRAG de Tarefas

**Módulo**: `menir_core/rag/tasks`
**Versão alvo**: ≥ v1.1 (após v1.0-system-core)

## 1. Objetivo

Este módulo implementa o **GraphRAG de Tarefas do Menir**: uma camada de leitura em cima do System Graph (Neo4j) que permite responder, de forma estruturada, perguntas sobre:

*   Sessões (`:Session`)
*   Projetos (`:Project`)
*   Tarefas (`:Task`)

Usando o grafo como **memória executiva** do sistema, e não apenas como armazenamento.

**Princípios:**
*   **Read-only**: este módulo não cria nem altera sessões/tarefas; apenas lê o grafo.
*   **Templates fixos**: as consultas são baseadas em intents e templates Cypher predefinidos, não em geração arbitrária de Cypher.
*   **Logs continuam canônicos**: `menir_sessions.jsonl` e `menir_tasks.jsonl` seguem sendo a verdade primária; o grafo é derivado via `scripts/sync_system_graph.py`.

---

## 2. Entidades e Relações (Resumo)

O módulo assume a existência, em Neo4j, de:
*   `(:Session {session_id, started_at, ended_at, state, exit_summary, operator, ...})`
*   `(:Project {project_id, name, status, ...})`
*   `(:Task {task_id, description, status, priority, created_at, project_id, ...})`

**Relações mínimas:**
*   `(:Session)-[:CREATED_TASK]->(:Task)`
*   `(:Project)-[:HAS_TASK]->(:Task)`
*   `(:Session)-[:FOCUSED_ON {primary: true}]->(:Project)`

Esses dados são alimentados exclusivamente por:
*   `scripts/boot_menir.py`
*   `scripts/shutdown_menir.py`
*   `scripts/sync_system_graph.py`

---

## 3. Intents do GraphRAG de Tarefas

Cada **intent** representa um tipo de pergunta que o sistema sabe responder sobre o grafo de tarefas. A camada LLM (Menir “agente”) só precisa escolher o intent correto e preencher parâmetros.

### 3.1. PROJECT_OPEN_TASKS
**Finalidade**: listar tarefas abertas de um projeto específico.

*   **Perguntas típicas**:
    *   “Quais tarefas abertas no projeto Débora?”
    *   “O que ainda está pendente no menir_core?”
*   **Parâmetros**:
    *   `project_id`: str – ex.: "debora", "menir_core", "general"
*   **Saída esperada (conceitual)**:
    *   Lista de objetos com: `task_id`, `description`, `status`, `priority`, `created_at`, `idade em dias`.
*   **Uso**: Base para respostas curtas tipo “O projeto Débora tem 3 tarefas abertas: …”.

### 3.2. PROJECT_SUMMARY
**Finalidade**: resumo de estado de um projeto (healthcheck leve).

*   **Perguntas típicas**:
    *   “Como está o projeto Débora?”
    *   “Resumo do estado do Menir Core.”
*   **Parâmetros**:
    *   `project_id`: str
*   **Saída esperada**:
    *   `project_info`: `project_id`, `name`, `status`
    *   `tasks_stats`: `open_count`, `done_count`, `blocked_count`, `oldest_open_age_days`
    *   `activity`: sessões recentes relacionadas ao projeto (Session-[:FOCUSED_ON]->Project)
*   **Uso**: “Projeto Débora está ACTIVE com 3 tarefas abertas, nenhuma bloqueada, última atividade há 2 dias...”

### 3.3. LAST_SESSION_TASKS
**Finalidade**: recuperar o que foi promovido a tarefa na última sessão.

*   **Perguntas típicas**:
    *   “O que foi criado na última sessão?”
    *   “Quais tarefas saíram do último shutdown?”
*   **Parâmetros**:
    *   `session_ref`: str – valores aceitos: `"last"` ou `session_id` explícito.
*   **Saída esperada**:
    *   `session`: `session_id`, `started_at`, `ended_at`, `state`, `exit_summary`
    *   `tasks_created`: lista de tarefas.
*   **Uso**: Para lembrar “o que foi combinado ontem” sem depender da memória da conversa.

### 3.4. STALE_TASKS
**Finalidade**: detectar tarefas “apodrecendo” no backlog.

*   **Perguntas típicas**:
    *   “Quais tarefas estão paradas há mais de 7 dias?”
*   **Parâmetros**:
    *   `min_age_days`: int
    *   `project_id` (opcional)
*   **Saída esperada**:
    *   Lista de tarefas com `age_days`.
*   **Uso**: “Essas 3 tarefas estão abertas há mais de 10 dias; sugerido priorizar ou encerrar.”

### 3.5. PROJECT_ACTIVITY_TIMELINE (fase 2)
**Finalidade**: enxergar a linha do tempo de sessões e tarefas de um projeto.

---

## 4. Contrato do Módulo (`menir_core/rag/tasks`)

### 4.1. Função de alto nível

```python
def query_tasks_graph(intent: str, **params) -> dict:
    ...
```

*   **intent**: "PROJECT_OPEN_TASKS", "PROJECT_SUMMARY", "LAST_SESSION_TASKS", "STALE_TASKS".
*   **params**: dicionário de parâmetros específicos do intent.
*   **Retorno**: `dict` estruturado (não texto pronto).

### 4.2. Requisitos de implementação
1.  Usar exclusivamente as entidades `Session`/`Task`/`Project`.
2.  **Read-Only**: Somente comandos `MATCH`, `WHERE`, `RETURN`.
3.  **Error Handling**: Retornar `dict` com `error: {code, message}` em vez de exceção bruta.

---

## 5. Roadmap imediato
1.  Subir o Neo4j Desktop.
2.  Rodar `python scripts/sync_system_graph.py` (garantir populado).
3.  Implementar `menir_core/rag/tasks.py` seguindo este contrato.
