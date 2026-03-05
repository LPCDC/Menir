<div align="center">
  <h1>🏔️ Menir OS v5.2</h1>
  <p><strong>The Sovereign, Metacognitive Graph Intelligence & Personal Zero-Trust Engine.</strong></p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Platform: Neo4j](https://img.shields.io/badge/Graph_Engine-Neo4j-008cc1?logo=neo4j)](https://neo4j.com/)
  [![Language: Python 3.12](https://img.shields.io/badge/Language-Python_3.12-blue?logo=python)](https://python.org)
  [![Frontend: React TS](https://img.shields.io/badge/Tier_2-Vite_React_TS-61DAFB?logo=react)](https://reactjs.org)
</div>

<br>

> *"Data acts as a vector; logic acts as a scalar. Only the Graph Remembers."* — **The Menir Manifesto**

## 📖 What is Menir?

**Menir** is not a simple LLM wrapper or automation script. It is a **Sovereign Graph Intelligence** hosted locally (`Neo4j`), designed with a *Zero-Trust* and *Zero-Bloat* architecture. It acts as a structural "Second Brain", forcing the fluidity of Artificial Intelligence (Google Gemini) to operate under the strict mathematical rules of graphs and rigorous validation (Pydantic V2).

It never forgets, never hallucinates critical data, and imposes absolute barriers for context isolation (Galvanic Isolation). Menir transforms the noise of daily and academic life into a routable and persistent ontology.

---

## ⚡ True Potential & Use Cases (Student & Researcher)

The Menir ecosystem was forged to combat digital amnesia, perfectly serving **Personal Life (Metacognition)**, academic research, and fluid life management.

### 1. The Metacognitive "Second Brain" (Academic Management)
Instead of relying on volatile vector databases or scattered notebooks, Menir plots your academic life into a Structured Neo4j Ontology.
- **Rapid Epistemic Ingestion:** You submit a dense PDF paper, class notes, or audio transcripts. Menir extracts concepts and mathematically connects the ideas: `(:Concept {name: "Machine Learning"})-[:IS_FOUNDATIONAL_TO]->(:ResearchTopic {title: "Neural Networks"})`.
- **Non-Linear Traceability:** Months later, if you ask *"Which authors did I read that disagree with the theory I studied last semester about convolutional networks?"*, Menir traverses the Graph. The database injects the entire historical bibliographic tree into the LLM's context window. It has syntactic empathy and structural memory.

### 2. The Task Routing and Absorption Engine
This core engine solves the problem of "forgotten deadlines" and information chaos:
- **Use Case:** You input a course syllabus or a messy thesis schedule.
- **Hallucination Barrier (Pydantic):** The LLM will never invent a delivery date. If the extracted date does not mathematically align with the system's temporal logic, the `Pydantic` barrier in Tier 1 destroys the payload. Only the absolute truth enters the temporal Graph (`[:DUE_BY]`).

### 3. Tier 2: Zero-Bloat Dashboard (React + TypeScript)
A dashboard derived directly from the Backend's mathematical specifications, ensuring total end-to-end synergy without the common "bloat" of modern web apps.
- Pure visualization of study deadlines and the map of acquired knowledge.
- Render-blocking Security powered by JWT authentication, ensuring your personal and intellectual notes remain inaccessible to third parties.

---

## ⚙️ Technical Paradigm

Menir bridges the gap between the abstract (AI) and the concrete (Graph Mathematics).

* **Graph Source of Truth:** `Neo4j` dictates reality. If the AI attempts to invent an author already registered with a slightly different name (e.g., "J. Doe" vs "John Doe"), the Cypher layer forces it back to the known UUID via semantic vector RAG (768-dimensions).
* **A.I. Engine:** Google `gemini-2.5-flash` operating primarily in `JSON_OBJECT` mode via MenirIntel. Shielded asynchronous generation (`asyncio.to_thread`).
* **Rigorous Typing:** MyPy em progresso: 53 erros baseline em resolução e strict Pydantic validation (`extra="forbid"` for ingestion edges).
* **Security & Isolation:** *Privacy by Design*. Capacity to completely segregate different "Life Modes" (Studies, Personal Finances, Work) through watertight "Tenants" managed by persistence in Python's local Context (`ContextVars`), preventing graph leakage.

---

## 📦 Node Initialization (Quickstart)

Requirements: **Neo4j AuraDB** (or local 5.x) and a **Google Gemini API Key**. Node.js `v20+` for the Client Layer.

1. **Clone & Environment:**
   ```bash
   git clone https://github.com/LPCDC/Menir.git
   cd Menir
   # Define NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, GOOGLE_API_KEY in your .env
   ```

2. **Graph Genesis (Bootstrap):**
   ```bash
   python -c "from src.v3.meta_cognition import MenirOntologyManager; import os; MenirOntologyManager(os.getenv('NEO4J_URI'), (os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD') or '')).bootstrap_system_graph()"
   ```

3. **Ignite Tier 1 (Synapse & Control Plane):**
   ```bash
   python src/v3/core/menir_runner.py
   ```

4. **Ignite Tier 2 (Client SPA):**
   ```bash
   cd menir_web
   npm run dev
   ```

<BR>
<div align="center">
  <i>"In Menir, nothing is lost. The Graph observes everything and remembers everything."</i>
</div>
