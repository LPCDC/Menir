# Snapshot Canônico: Menir System v1.0 (Transition to v1.1)

**Referência**: Tag `v1.0` | Infra: AuraDB | Data: 10/12/2025

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

Objetivos imediatos já implementados ("Beta v1.1"):
- [x] CLI Unificado (`menir_cli.py`).
- [x] API Python Agente-Grafo.
- [x] Health Check.

Próximos passos (v1.2+):
- [ ] Transformar em Daemon/Service.
- [ ] Dashboard Web.
- [ ] Integração com Calendário.

---
*Este documento reflete o estado do sistema em sua transição pós-v1.0 release.*
