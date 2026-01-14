# Manual do Operador Menir v1.0

*(System Core + Task GraphRAG + AuraDB)*

---

## 0. Objetivo

Este manual descreve **como operar o Menir como “Sistema Operacional”**, usando:

- **Eixo de Sessões (Jornal)**  
  - `scripts/boot_menir.py`  
  - `scripts/shutdown_menir.py`  
  - `data/system/menir_sessions.jsonl`  
  - `data/system/menir_tasks.jsonl`

- **Eixo de Grafo (Corpo)**  
  - `scripts/sync_system_graph.py` + Neo4j AuraDB

- **Task GraphRAG (Cérebro Executivo)**  
  - `menir_core/rag/tasks.py`  
  - `scripts/query_menir.py`

Foco: **rotina prática de uso**, não detalhes internos de código.

---

## 1. Pré-requisitos

- Repositório `Menir` clonado/local no PC.
- Python instalado e funcional.
- Ambiente virtual configurado (se aplicável).
- Arquivo `.env` na raiz do repo com, no mínimo:

```env
NEO4J_URI=neo4j+s://<seu-cluster>.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=<senha-do-neo4j-aura>
NEO4J_DB=neo4j
OPENAI_API_KEY=<sua-chave>
DEFAULT_PROJECT=debora
```

Cluster AuraDB online e acessível com essas credenciais.

---

## 2. Conceitos de Operação

**Sessão Menir**  
Unidade de trabalho entre um `boot_menir.py` e um `shutdown_menir.py`.  
Cada sessão gera um registro em `data/system/menir_sessions.jsonl`.

**Tarefa Menir**  
Decisão/ação promovida no final da sessão.  
Registrada em `data/system/menir_tasks.jsonl`.  
Cada tarefa está ligada a um projeto (ex.: debora, menir_core, general).

**Projeto Âncora**  
Macro-contextos permanentes (Itaú, Débora, Tivoli, Iberê, Saint Charles, Menir Core etc.).  
No grafo, são nós `(:Project)`.

**System Graph**  
Projeção das sessões e tarefas na AuraDB:  
`(:Session)`, `(:Task)`, `(:Project)` + relacionamentos.

**Task GraphRAG**  
Camada de leitura inteligente do grafo.  
Responde perguntas como “quais tarefas abertas no projeto Débora?”.

---

## 3. Fluxo Diário de Uso (PC)

### 3.1. Início de bloco de trabalho (Boot)

1. Abrir o VS Code no diretório do Menir.
2. Abrir o Terminal integrado (Menu Terminal → New Terminal).  
   *O terminal já abre na raiz do projeto.*
3. Executar:
   ```bash
   python scripts/boot_menir.py
   ```

**O que acontece:**
*   Verifica a última sessão (CLEAN, CRASHED ou primeira vez).
*   Cria uma nova `session_id` e grava em `menir_sessions.jsonl`.
*   Carrega as tarefas abertas de `menir_tasks.jsonl` e mostra um snapshot.
*   Tenta sincronizar o grafo (chamando `sync_system_graph.py`).

**Em paralelo, na interface de chat (Menir/Peposo):**
*   Digitar `boot now` para alinhar o contexto conversacional com o estado do sistema.

### 3.2. Durante a sessão

*   Usar o Menir normalmente (projetos, decisões, brainstorms).
*   Não é obrigatório registrar cada coisa na hora; o registro oficial acontece no shutdown.
*   Se algo for crítico, pode anotar numa nota rápida para lembrar no final.

### 3.3. Encerramento do bloco/dia (Shutdown)

No **MESMO terminal** em que você rodou o boot:
```bash
python scripts/shutdown_menir.py
```

**Fluxo:**
1.  O script identifica a sessão atual via `.menir_state`.
2.  Solicita um **resumo da sessão**:  
    Ex.: “Revisamos o Cap.1 da Débora, definimos 2 tarefas para Menir Core”.
3.  Solicita **tarefas a promover** no formato:
    ```
    projeto: descrição
    ```
    Exemplos:
    *   `debora: revisar final do capitulo 1`
    *   `menir_core: documentar status cli`
    *   `general: organizar pastas de referencia`

4.  Para cada linha:
    *   Cria uma `task_id`; grava em `menir_tasks.jsonl` com status OPEN.
2.  Atualiza a sessão para CLOSED em `menir_sessions.jsonl` com timestamp_end e exit_summary.
3.  Chama `sync_system_graph.py` para projetar tudo em AuraDB.
4.  Remove `.menir_state`.

**Resultado:**
*   Sessão encerrada.
*   Tarefas oficializadas.
*   Grafo sincronizado com AuraDB.

---

## 4. Consultando o Estado do Sistema (Task GraphRAG)

Para perguntar o estado direto ao grafo (via terminal):

### 4.1. Resumo do Menir Core
```bash
python scripts/query_menir.py summary menir_core
```
*Retorna algo como:*
*   Nome do projeto
*   Quantidade de tarefas abertas / concluídas
*   Eventuais estatísticas adicionais

### 4.2. Tarefas abertas de Débora
```bash
python scripts/query_menir.py open debora
```
*Lista tarefas OPEN do projeto debora com descrição, prioridade, datas, etc.*

### 4.3. Tarefas criadas na última sessão
```bash
python scripts/query_menir.py last
```
*Mostra quais tarefas foram criadas no último `shutdown_menir.py`.*

### 4.4. Tarefas antigas (“stale”) – se implementado
```bash
python scripts/query_menir.py stale 7
```
*Lista tarefas abertas há mais de 7 dias (ou o número fornecido).*

---

## Próximas Ações Sugeridas
1.  Usar `boot`/`shutdown` em todo bloco de trabalho para popular o histórico (logs + grafo).
2.  Ensinar o agente a consultar `query_tasks_graph` antes de responder “não sei”.
