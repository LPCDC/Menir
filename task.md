# Menir – Task Board

> Versão de referência: v1.0-system-core (concluída)

Este arquivo registra o backlog evolutivo do Menir **a partir** da v1.0, para organizar futuras melhorias e evoluções.

---

## 1. Estado Atual (v1.0 – Concluído)

- [x] Eixo de Sessões (boot/shutdown + JSONL de sessões e tarefas).  
- [x] Eixo de Grafo (sync para AuraDB, System Graph com Session/Task/Project).  
- [x] Task GraphRAG (queries de estado e CLI `query_menir.py`).  
- [x] Manual do Operador (`docs/MANUAL_OPERADOR_MENIR_v1.0.md`).

---

## 2. Próxima Versão – v1.1 (Ergonomia & Status)

### 2.1. Ergonomia de CLI

- [x] Criar CLI unificado (ex.: `menir_cli.py`) com subcomandos:  
  - `menir boot` → invoca `boot_menir.py`  
  - `menir shutdown` → invoca `shutdown_menir.py`  
  - `menir status` → usa Task GraphRAG para mostrar:
    - sessões recentes  
    - tarefas abertas por projeto  
    - tarefas “stale”  

- [x] Criar comando `menir health` para:
  - testar conexão com AuraDB (`scripts/check_db_auth.py`)  
  - verificar contagem de Session/Task no grafo vs JSONL  

### 2.2. Integração Agente ↔ GraphRAG

- [x] Fazer o agente Menir consultar automaticamente o grafo (via GraphRAG) antes de responder “não sei” sobre estado de projeto.  
- [x] Definir protocolo claro: 
  - AG gera um Snapshot Canônico após cada mudança no repo/infra;  
  - Peposo consome esse snapshot como base de contexto.  

---

## 3. Ideias Futuras – v2.x (Exploratório)

- [ ] Transformar o Menir em daemon ou servidor sempre ligado, para permitir acesso remoto (ex: via celular).  
- [ ] Integrar com calendário/agenda (Google Calendar ou outro), para vincular sessões/tarefas às janelas de tempo real.  
- [ ] Criar dashboard web para o grafo: mostrar visualmente sessões, tarefas, projetos, backlog.  
