# Snapshot Canônico: Menir System v1.1 (Release)

**Referência**: Tag `v1.1.0` | Infra: AuraDB | Data: 10/12/2025

---

## 1. Arquitetura do Sistema

O Menir é um Sistema Operacional Pessoal composto por três eixos integrados:

### A. Eixo de Sessões (Jornal)
*   **Scripts**: `boot_menir.py` (Início), `shutdown_menir.py` (Fim).
*   **Dados**: `data/system/menir_sessions.jsonl` (Log auditável).
*   **Fluxo**: Work Session cria `session_id`, Task Promotion no shutdown gera `task_id`.

### B. Eixo de Grafo (Corpo)
*   **Infra**: Neo4j AuraDB (Cloud).
*   **Sync**: `scripts/sync_system_graph.py` projeta Logs JSONL → Nós Graph.
*   **Modelo**: `(:Session)-[:CREATED]->(:Task)`, `(:Session)-[:FOCUSED_ON]->(:Project)`.

### C. Task GraphRAG (Cérebro Executivo)
*   **Motor**: `menir_core/rag/tasks.py` (Leitura inteligente).
*   **API**: `get_project_state()`, `list_open_tasks()`.
*   **CLI**: `scripts/menir_cli.py` (Orquestrador unificado).

---

## 2. Playbook de Operação (v1.1)

O fluxo operacional foi unificado via `menir_cli.py`.

### Comandos Principais
*   **Boot**: `python scripts/menir_cli.py boot`
    *   *Inicia sessão e sincroniza.*
*   **Health**: `python scripts/menir_cli.py health`
    *   *Verifica Banco e Logs.*
*   **Status**: `python scripts/menir_cli.py summary debora`
    *   *Resumo de projeto.*
*   **Shutdown**: `python scripts/menir_cli.py shutdown`
    *   *Encerra e promove tarefas.*

---

## 3. Estado da Infraestrutura

*   **Conexão**: AuraDB (`neo4j+s://14dc1764...`).
*   **Configuração**: Arquivo `.env` (não versionado) na raiz.
*   **Status**: Online e Validado via `menir_health.py`.

---

## 4. Backlog de Evolução (v1.1)

Objetivos agora implementados ("Stable v1.1"):
- [x] CLI Unificado (`menir_cli.py`).
- [x] API Python Agente-Grafo.
- [x] Health Check.
- [x] MCP Server Validado.

Próximos passos (v1.2+):
- [ ] Transformar em Daemon/Service.
- [ ] Dashboard Web.
- [ ] Integração com Calendário.

---

## 5. MCP Server (JSON-RPC + FastAPI)

A partir da v1.1, o Menir passa a expor um servidor MCP (Model Context Protocol) próprio, implementado em FastAPI e validado por 21 testes automatizados.

### 5.1. Stack e localização

- Módulo principal: `menir10/mcp_app.py`
- Framework HTTP: FastAPI (declarado em `requirements.txt`)
- Protocolo de chamada: JSON-RPC 2.0 sobre HTTP

### 5.2. Endpoints HTTP

- `GET /health`  
  - Verifica se o servidor está operacional.  
  - Retorno típico: `{"status": "ok"}` (HTTP 200).

- `GET /info`  
  - Exibe metadados do MCP server (nome, versão lógica, etc.).  
  - Usado pelos testes para garantir que o servidor está configurado corretamente.

### 5.3. Métodos JSON-RPC principais

Os métodos abaixo são expostos via JSON-RPC (normalmente em um endpoint único, ex.: `POST /mcp`):

- `boot_now`  
  - Dispara um “boot” lógico do Menir, retornando informações de sessão/projeto relevantes para inicialização.

- `list_projects`  
  - Lista projetos conhecidos pelo sistema (como Itaú, Tivoli, Iberê, Livro Débora, Saint Charles, etc.), em formato estruturado.

- `project_summary`  
  - Retorna um resumo sintético de um projeto específico, incluindo contagem de tarefas e últimas interações.

- `search_interactions`  
  - Realiza busca em interações/diário do Menir e devolve um conjunto de eventos recentes relacionados ao critério de busca.

- `context` (quando disponível nos testes)  
  - Retorna um bloco de contexto com chaves padronizadas, por exemplo:
    - `project_id`
    - `interaction_count`
    - `recent_interactions` (lista de eventos resumidos)

### 5.4. Convenções de erro e contratos

- Métodos desconhecidos: retornam HTTP 404.  
- Requisições JSON inválidas ou malformadas: retornam HTTP 400, via handler dedicado de validação.  
- Estrutura de resposta segue o contrato verificado pelos testes (`21 passed`), garantindo compatibilidade com clientes MCP que falem JSON-RPC 2.0.

### 5.5. Estado de validação

- Suite de testes: `tests/test_mcp_server.py`  
- Resultado atual: **21 passed, 3 warnings**.  
- Isso garante que o MCP Server está alinhado com o contrato funcional da versão v1.1 e pronto para ser consumido por agentes externos (Menir no GPT-5, plugins MCP, etc.).

---
*Este documento reflete o estado do sistema na release v1.1.*
