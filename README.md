<div align="center">
  <h1>🏔️ Menir Core</h1>
  <p><strong>A Sovereign, Metacognitive Second Brain & Holistic Graph Intelligence.</strong></p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Platform: Neo4j](https://img.shields.io/badge/Graph_Engine-Neo4j-008cc1?logo=neo4j)](https://neo4j.com/)
  [![Language: Python 3.12](https://img.shields.io/badge/Language-Python_3.12-blue?logo=python)](https://python.org)
</div>

<br>

> *"Data acts as a vector; logic acts as a scalar."* — **The Menir Manifesto**

## 📖 The "Immortal" Second Brain

**Menir** is not an app, a simple LLM wrapper, or merely a financial script. It is a **Sovereign, Self-Hosted Graph Intelligence** built to be the absolute, immutable "Second Brain" of its creator and their encompassing ecosystems. 

Unlike stateless Agentic workflows that forget who you are every time the chat closes, Menir encodes every relationship, memory, document, and interaction into a deterministic localized **Neo4j Ontology**. It never forgets a person, never misplaces a memory, and structurally enforces truth over hallucination.

### 🧠 The Core: Jungian Metacognition & Personal Ontology
Menir is imbued with distinct, operative psychological profiles that alter how the engine perceives and responds to the data it ingests:
* **Jungian Personas:** The core operates under specific ontological masks (e.g., the rigorous, clinical `DEFAULT_MENIR` vs. the empathetic, collaborative `PEPOSO_OVERRIDE`).
* **Relational Cartography:** It maps the user's life by creating dynamic `(:Person)` and `(:Relationship)` nodes. It understands human interconnections, professional projects, and even astrological archetypes across its extensions.
* **Persistent Empathy & Memory:** Experiences, warnings, and nuanced notes are permanently grafted as properties onto the Graph. When Menir speaks to you, it remembers your history, your exact tax structure, and your personal connections without relying on fragile vector-cloud context windows.

---

## 💼 The Professional Layer: Multi-Tenant Enterprise Capabilities (V5.2)

Because the core engine is so mathematically rigid and contextually aware, Menir is uniquely capable of managing highly complex B2B ecosystems via absolute **Galvanic Isolation**—meaning the same "Brain" that manages a personal life can concurrently automate the accounting for multiple Swiss fiduciaries (Tenants) without cross-contamination.

### ✨ FinTech & ERP Features
* **Pydantic Fiduciary Shields:** It routes financial documents (Invoices, Receipts) through strict validation layers. It mathematically rejects hallucinations: if an invoice subtotal plus the dynamic TVA rate doesn't match the total, the graph rejects it.
* **Temporal Meta-Ontology:** Menir dynamically reads tax frameworks (like the Swiss ESTV rates) directly from the Graph based on the document's issue date to prevent temporal anachronisms.
* **Bimodal Visual Extraction:** 
  * `FAST_LANE`: Instantly shreds native text PDFs (pypdf) at zero cost.
  * `SLOW_LANE`: Downgrades to Vision API (gemini-2.5-flash) for scans/physical receipts in the wild.
* **Cypher Reconciliation Engine:** A completely automated pipeline running inside Neo4j that calculates magnitude deltas to autonomously match Invoices against deterministic `camt.053` Bank XML Transactions.
* **Swiss nFADP Compliant:** Operates on absolute data sovereignty, with LLM routes mapped carefully to ensure no PII leaks into generalized cloud training sets.

---

## ⚙️ Technical Paradigm

Menir bridges the gap between the fluid (Generative AI) and the concrete (Graph Mathematics).

* **Graph Source of Truth:** `Neo4j` dictates everything. If the API hallucinates an entity name, the strict Cypher merge layer forces it back into conformity based on known UUIDs and Aliases.
* **A.I. Engine:** Google `gemini-2.5-flash` natively integrated with forced JSON structured inference. 
* **Validation:** Explicit Python `pydantic` validators governing everything from MOD11 Swiss VAT checks to human relationship deduplication.
* **Environment:** Python 3.12, Docker-Compose (hardened read-only volumes for sovereignty).

---

## 📦 Quickstart

Menir requires a dedicated **Neo4j AuraDB** (or a local Dockerized Neo4j 5.x) and a **Google Gemini API Key**.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LPCDC/Menir.git
   cd Menir
   ```

2. **Set up the Environment:**
   ```env
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_secure_password
   NEO4J_DB=neo4j
   GOOGLE_API_KEY=your_gemini_api_key
   ```

3. **Initialize the Kernel (Ontology Bootstrap):**
   ```bash
   python -c "from src.v3.meta_cognition import MenirOntologyManager; import os; MenirOntologyManager(os.getenv('NEO4J_URI'), (os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))).bootstrap_system_graph()"
   ```

4. **Start the Menir Async Engine:**
   ```bash
   python src/v3/core/menir_runner.py
   ```

---

<div align="center">
  <i>"Menir sees the Graph. The Graph Remembers."</i>
</div>
