> Fonte arquitetural canônica do Menir OS — Para Claude (Arquiteto) e AG (Executor)
> Versão: V5.2 | Atualizado: 05/03/2026

---

## IDENTIDADE DO SISTEMA

**Menir OS** é um "Cognitive Financial & Ontological Kernel" — não um ERP, CRM ou software de contabilidade.
É uma camada de orquestração AI multi-tenant, assíncrona, construída sobre Neo4j como Knowledge Graph soberano.

**Mantra:** *"Data acts as a vector; logic acts as a scalar. Only the Graph Remembers."*

---

## STACK TECNOLÓGICO (estado atual)

| Camada | Tecnologia | Observação |
|--------|-----------|------------|
| Graph DB | Neo4j Aura Free | Sem RBAC nativo — usar MCPQueryGuard |
| Backend | FastAPI + uvicorn | Migrado de aiohttp |
| LLM | google-genai>=1.0.0 | gemini-2.5-flash (inferência) |
| Embedding | gemini-embedding-001 | 768-dim, output_dimensionality=768 |
| Validação | Pydantic V2 (>=2.7.0) | extra="forbid" em schemas de entrada |
| Async | asyncio + aiohttp | to_thread para I/O síncrono |
| Resilience | Tenacity | retry exponential em toda chamada externa |
| Auth | PyJWT>=2.8.0 | Galvanic Isolation via JWT + ContextVar |
| MCP | mcp[cli]>=1.0.0 | READ_ONLY=true + MCPQueryGuard |
| Frontend | React + Vite + TypeScript | openapi-typescript → schema.d.ts |
| Astro Ext | flatlib>=0.2.3 | Extensão pessoal — degradação graciosa |

**SDK MORTA — NUNCA USAR:**
- `google-generativeai` (EOL Nov/2025)
- `vertexai` / `vertexai.generative_models` (remover de menir_intel.py)
- `text-embedding-004` (desligado 14/Jan/2026)

---

## TENANTS

### BECO (prioridade de receita)
- **O que é:** Fiduciária suíça operada por Ana Paula (prima) e Nicole (afilhada)
- **Domínio:** Invoice, BankTransaction, TaxRule, Vendor, CamtFile
- **Compliance:** nFADP, FINMA Circ. 2023/1, Swiss UID MOD11
- **TVA rates:** 8.1% (standard), 3.8% (hospitality), 2.6% (reduced)
- **Moedas:** CHF, EUR
- **Output:** Crésus ERP (via cresus_exporter.py)
- **Status:** MVP — invoice_skill precisa de lógica real

### SANTOS (laboratório de modelo)
- **O que é:** Tenant pessoal — Ana Caroline Albuquerque (talks corporativos)
- **Domínio:** Lead, Event, Product, Channel, Concept, TargetAudience
- **Produto:** "A Beleza do Equilíbrio" — burnout/NR-1 compliance
- **Status:** Bootstrap completo, LeadSkill ativa, vector indexes operantes

---

## PRINCÍPIOS ARQUITETURAIS INVIOLÁVEIS

### 1. Isolamento Galvânico
```python
# CORRETO — ContextVar como única fonte de verdade
with locked_tenant_context("BECO"):
    await process_document(path)

# PROIBIDO — tenant como parâmetro (anti-pattern)
await process_document(path, tenant_id="BECO")

# OBRIGATÓRIO — se não há contexto, abortar
tenant = TenantContext.get()
if not tenant:
    raise RuntimeError("Operação fora de contexto galvânico")
```

### 2. Todo nó DEVE ter âncora de tenant
```cypher
MERGE (n:Label {id: $id})
MATCH (t:Tenant {name: $tenant})
MERGE (n)-[:BELONGS_TO_TENANT]->(t)
```

### 3. Schemas Pydantic
```python
# Entrada de LLM — sempre forbid
class InvoiceData(BaseModel):
    model_config = ConfigDict(extra="forbid")

# Saída do grafo — pode ser allow
class InvoiceDataFromGraph(InvoiceData):
    model_config = ConfigDict(extra="allow")
```

### 4. I/O assíncrono
```python
# Neo4j em contexto async
result = await asyncio.to_thread(lambda: session.run(query, **params))

# Fire-and-forget para enhancements
asyncio.create_task(EmbeddingService.embed_and_persist(...))
```

### 5. Confiar no repo quando contradizer documentação
Se `mypy_report.txt` diz 53 erros e README diz 0 — o repo tem razão.

---

## DOIS NÓS RAIZ DO GRAFO

```cypher
// Raiz sistêmica — o que o Menir É
(:Menir {uid: "MENIR_CORE", version: "5.2"})

// Raiz humana — para quem o Menir EXISTE
(:User:Person {uid: "luiz", name: "Luiz", role: "OWNER"})

// Relação de gênese
(:Menir)-[:SERVES_USER]->(:User)
(:User)-[:IS_SERVED_BY]->(:Menir)
```

O (:Menir) é meta-camada — não pertence a nenhum tenant.
O (:User) é evolutivo — muda de projetos, colaboradores, crenças.

---

## MÓDULOS PRINCIPAIS

```
src/v3/
├── core/
│   ├── menir_runner.py      # Entry point do sistema
│   ├── synapse.py           # HTTP + command_bus (FastAPI)
│   ├── logos.py             # CommandPayload + origins tipadas
│   ├── meta_cognition.py    # MenirOntologyManager + bootstrap
│   ├── reconciliation.py    # Cruzamento invoice × camt.053
│   ├── cresus_exporter.py   # Output para Swiss Crésus ERP
│   ├── provenance.py        # Rastreamento de origem dos dados
│   └── schemas/
│       └── identity.py      # ContextVar de tenant
├── menir_intel.py           # LLM engine (gemini-2.5-flash)
├── menir_bridge.py          # TenantAwareDriver
├── skills/
│   ├── invoice_skill.py     # BECO — extração de faturas (incompleto)
│   └── lead_skill.py        # SANTOS — captura e embedding de leads
├── mcp/
│   ├── server.py            # MCP server (READ_ONLY)
│   ├── security.py          # MCPQueryGuard
│   └── protools.py          # MCP tools expostos
└── extensions/
    └── astro/               # Módulo pessoal — flatlib
        ├── engine.py        # MenirAstro
        ├── time_engine.py   # MenirTime
        ├── schema.py        # BirthChart, Placement
        └── genesis.py       # Criação de Person com papéis
```

---

## CONTEXTO ESTRATÉGICO

| Dimensão | Estado |
|---------|--------|
| Runway | Meses — BECO é a prioridade absoluta |
| Modelo de negócio | Setup fee (CHF 5-15k) + mensalidade (CHF 500-2k) |
| Defensibilidade | Lock-in ontológico — grafo acumulado é irreplaceable |
| BECO blocker atual | invoice_skill sem lógica real de extração suíça |
| Frontend | React Tier 2 — Auth bridge ativo, dashboard pendente (Fase 44) |
| Expansão pessoal | Dois nós raiz planejados — após mypy zerado |

---

## AG — PROTOCOLO DE SESSÃO

```
1. Ler MENIR_STATE.md → anunciar fingerprint
2. Verificar config.py (modelos SDK)
3. Verificar nós BECO duplicados no Neo4j
4. Carregar skills por contexto da tarefa
5. Ao concluir: atualizar MENIR_STATE.md + commit
```

---

*Gerado por: Claude (Arquiteto Principal) | 05/03/2026*
