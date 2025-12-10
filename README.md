# Menir — Semantic Narrative System

## Versão atual: **v1.0 – System Core + Task GraphRAG**

Menir é agora um sistema operacional pessoal completo, com:

- 🎯 **Eixo de Sessões**: ciclo Boot → Trabalho → Shutdown, com histórico auditável.  
- 🧠 **Task GraphRAG**: grafo de sessões/tarefas em Neo4j Aura + queries de estado.  
- 📘 **Manual de Operador**: `docs/MANUAL_OPERADOR_MENIR_v1.0.md`.  
- 📋 **Backlog para futuras evoluções**: `task.md`.  

---

## Começando a usar (fluxo mínimo)

### 1. Preparação

- Clone este repositório.  
- Garanta que o arquivo `.env` esteja configurado com credenciais válidas do Neo4j AuraDB e da OpenAI.  
- Instale dependências Python, se houver.

### 2. Iniciar um bloco de trabalho

```bash
python scripts/boot_menir.py
```

### 3. Encerrar um bloco de trabalho

```bash
python scripts/shutdown_menir.py
```

### 4. Consultar o Sistema (GraphRAG)

```bash
python scripts/query_menir.py summary menir_core
python scripts/query_menir.py open debora
```

---
> *Menir v1.0 - Unindo Linguagem e Sistema.*
