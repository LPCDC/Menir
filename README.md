<div align="center">
  <h1>🏔️ Menir Core v5.2</h1>
  <p><strong>The Sovereign, Metacognitive Graph Intelligence & B2B Zero-Trust Engine.</strong></p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Platform: Neo4j](https://img.shields.io/badge/Graph_Engine-Neo4j-008cc1?logo=neo4j)](https://neo4j.com/)
  [![Language: Python 3.12](https://img.shields.io/badge/Language-Python_3.12-blue?logo=python)](https://python.org)
  [![Frontend: React TS](https://img.shields.io/badge/Tier_2-Vite_React_TS-61DAFB?logo=react)](https://reactjs.org)
</div>
<br>
<<<<<<< HEAD
> *"Data acts as a vector; logic acts as a scalar."* — **The Menir Manifesto**
> 
## ⚙️ Technical Paradigm
Menir bridges the gap between the fluid (Generative AI) and the concrete (Graph Mathematics).
* **Graph Source of Truth:** `Neo4j` dictates everything. If the API hallucinates an entity name, the strict Cypher merge layer forces it back into conformity based on known UUIDs and Aliases.
* **A.I. Engine:** Google `gemini-2.5-flash` natively integrated with forced JSON structured inference. 
* **Validation:** Explicit Python `pydantic` validators governing everything from MOD11 Swiss VAT checks to human relationship deduplication.
* **Environment:**
## 📖 The "Immortal" Second Brain
=======
> *"Data acts as a vector; logic acts as a scalar. Only the Graph Remembers."* — **The Menir Manifesto**
## 📖 O que é o Menir?
>>>>>>> d3e8ab2 (docs: Rewrite README emphasizing practical real-world B2B and Metacognitive applications)
**Menir** não é um mero wrapper de LLM ou um script de automação. É uma **Inteligência em Grafo Soberana** hospedada localmente (`Neo4j`), desenhada sob arquitetura *Zero-Trust* e *Zero-Bloat*. Ele age como um "Segundo Cérebro" estrutural, forçando a fluidez da Inteligência Artificial (Google Gemini 2.5) a operar sob as regras estritas da matemática de grafos e validação rigorosa (Pydantic V2).
Ele nunca esquece, nunca alucina em dados críticos e impõe barreiras absolutas de isolamento de contexto (Galvanic Isolation).
---
## ⚡ Potencial Real & Aplicabilidade
O ecossistema do Menir foi forjado para operar simultaneamente em dois extremos cognitivos: **A Vida Pessoal (Metacognição)** e o **Rigidez Corporativa (Swiss Fiduciary ERP)**.
### 1. Fiduciária Suíça Autônoma (Multi-Tenant B2B)
O motor resolve o problema crônico da alucinação de LLMs no setor financeiro usando a Arquitetura em Grafos:
- **Exemplo de Uso:** Você faz o upload de 50 faturas mistas (PDFs nativos e fotos amassadas). O Menir usa a `FAST_LANE` (PyPDF) para documentos digitais a custo zero e a `SLOW_LANE` (Gemini Vision) para extrair dados físicos pesados.
- **O Filtro de Alucinação:** Se o LLM alucinar o *Subtotal* e ele não bater com as taxas do IVA Suíço (TVA) somadas ao *Total*, a barreira matemática do `Pydantic` no Tier 1 destrói o payload com erro 422. Apenas a verdade absoluta entra no Grafo.
- **Isolamento Galvânico:** Todo tenant (Ex: *SANTOS* vs *BECO*) opera em túneis de memórias e rotas de código distintas usando `ContextVars`. É fisicamente impossível uma fatia de código da empresa A acessar os dados da empresa B.
- **Reconciliação Cypher Automática:** Ele cruza as faturas validadas do Grafo diretamente com os extratos bancários XML `camt.053` e gera o output blindado pronto para o Software de Contabilidade *Swiss Crésus ERP*.
### 2. O "Segundo Cérebro" Metacognitivo
Ao invés de depender de bancos vetoriais voláteis, o Menir plota a vida do usuário numa Ontologia Estruturada Neo4j.
- **Exemplo de Uso:** No chat, você menciona um novo projeto de consultoria com o "João". O Menir não salva um "log de texto". Ele intercepta a conversa, cria dinamicamente o Nó `(:Person {name: "João"})`, e gera a aresta matemática `(:User)-[:WORKS_WITH]->(:Person)`.
- Se meses depois você perguntar *"O que aconteceu com aquele sistema do João?"*, o Menir fará uma travessia no Grafo, e o banco injetará toda a árvore histórica do João diretamente na janela de contexto do LLM perfeitamente. Ele tem empatia algorítmica.
### 3. Tier 2: Enterprise Dashboard (React + TypeScript)
Painel Zero-bloat derivado diretamente das especificações matemáticas do Backend, garantindo total sinergia de ponta a ponta.
- Transpilação de AST direta de OpenAPI (`openapi-typescript`), garantindo que o DTO do banco de dados dita o tipo TypeScript no frontend, eliminando erros ou variáveis não mapeadas.
- Render-blocking Security (AuthGuard) alimentado pela autenticação de túnel JWT do Backend.
---
<<<<<<< HEAD
 Python 3.12, Docker-Compose (hardened read-only volumes for sovereignty).
=======
## ⚙️ Paradigma Técnico
Menir preenche o abismo entre o abstrato (AI) e o concreto (Matemática de Grafos).
* **Graph Source of Truth:** `Neo4j` dita a realidade. Se a IA tenta inventar o nome de uma empresa já registrada, a camada Cypher a força de volta para o UUID conhecido.
* **A.I. Engine:** Google `gemini-2.5-flash` operando primariamente em `JSON_OBJECT` mode via MenirIntel.
* **Typing Rigoroso:** MyPy Static Typing testado e fechado em 0 Erros em todos os mais de 35 módulos fonte.
* **Segurança:** Swiss nFADP (Nova Lei de Proteção de Dados da Suíça) *Privacy by Design*. Dados de Identidade Pessoal (PII) ofuscados, e processamento estritamente contido no Banco de Dados isolado.
>>>>>>> d3e8ab2 (docs: Rewrite README emphasizing practical real-world B2B and Metacognitive applications)
---
## 📦 Inicialização do Nó (Quickstart)
Requerimentos: **Neo4j AuraDB** (ou local 5.x) e **Google Gemini API Key**. Node.js `v20+` para a Camada Cliente.
1. **Clone & Ambiente:**
   ```bash
   git clone https://github.com/LPCDC/Menir.git
   cd Menir
   # Defina NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, GOOGLE_API_KEY no seu .env
   ```
2. **Gênese do Grafo (Bootstrap):**
   ```bash
   python -c "from src.v3.meta_cognition import MenirOntologyManager; import os; MenirOntologyManager(os.getenv('NEO4J_URI'), (os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD') or '')).bootstrap_system_graph()"
   ```
3. **Ignite Tier 1 (Synapse & Control Plane):**
   ```bash
   python src/v3/core/menir_runner.py
   ```
4. **Ignite Tier 2 (Enterprise SPA):**
   ```bash
   cd menir_web
   npm run dev
   ```
<BR>
<div align="center">
  <i>"No Menir, nada se perde. O Grafo a tudo assiste e a tudo lembra."</i>
</div>
