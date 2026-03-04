<div align="center">
  <h1>🏔️ Menir Core V5.2</h1>
  <p><strong>The Sovereign, Multi-Tenant Metacognitive ERP Architecture for Switzerland.</strong></p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Platform: Neo4j](https://img.shields.io/badge/Graph_Engine-Neo4j-008cc1?logo=neo4j)](https://neo4j.com/)
  [![Language: Python 3.12](https://img.shields.io/badge/Language-Python_3.12-blue?logo=python)](https://python.org)
  [![Swiss nFADP](https://img.shields.io/badge/Compliance-Swiss_nFADP-red?logo=swiss)](https://www.edoeb.admin.ch/)
</div>

<br>

## 🚀 Seeking Investment & Strategic Partners
**Menir Core is seeking Seed / Series A investments to transition from its battle-tested V5.2 Kernel into a fully-fledged, web-based enterprise B2B platform.**

We are looking for visionary partners, angel investors, and funds focused on **A.I., FinTech, and Enterprise SaaS** who understand the immense value of bringing sovereign, hallucination-free, and mathematically rigorous Graph RAG automation to the highly-regulated Swiss accounting and fiduciary markets.

If you are an investor, reach out to us at: **[Insert Contact Email / LinkedIn]**

---

## 📖 The "Operating System" for Fiduciaries

**Menir Core is NOT a custom script for a single client.** It is a vastly generalized, multi-tenant B2B platform. Think of it as an Operating System designed to automate complex bookkeeping, reconciliation, and audit pipelines for thousands of disparate Swiss fiduciaries simultaneously—all feeding into systems like the **Crésus ERP**.

By anchoring GenAI strictly into a rigid **Neo4j Ontology**, Menir forces AI to obey absolute mathematical laws and tenant-specific constraints, utterly eliminating the hallucination problems that plague traditional Agentic architectures.

### 🏢 True Multi-Tenancy (Plug-and-Play)
The system is built on **Galvanic Chart Isolation**:
* **Graph Separation:** Invoices and Bank Transactions are dynamically labeled upon ingestion (e.g., `(:Invoice:BECO)`, `(:Transaction:SANTOS)`). The Cypher Engine naturally segregates tenants at the node level, meaning zero cross-client data leakage without requiring separate clusters.
* **Tenant Parameterization:** Financial intelligence isn't hardcoded `IF/THEN`. The Oracles fetch tax catalogues dynamically from the Graph (`(t:Tenant)-[:HAS_TVA_RATE]->(r:TVARate)`). **Adding a new client from a different sector or country simply requires injecting their tax nodes into the Graph—zero code changes required to the Core.**
* **Semantic Anchoring:** We deploy `(:GoldenExample)` nodes bound to specific tenants. The LLM extracts specific edge-case formatting by mimicking its tenant's golden standards via Few-Shot styling.

### ✨ Architectural Features
* **Neo4j Temporal Meta-Ontology:** The Intelligence layer reads active tax framework constraints (e.g., Swiss ESTV TVA rates) based on the exact temporal issue-date of the document to prevent fiscal anachronisms.
* **Bimodal Intelligence (FAST_LANE & SLOW_LANE):** 
  * `FAST_LANE`: Shreds native PDF text-vectors (pypdf) at scale instantly.
  * `SLOW_LANE`: Intelligently downgrades to Vision API (gemini-2.5-flash) only for physical scans and photographs.
* **Pydantic Fiduciary Shields:** No invoice is committed to the Graph if the subtotal mismatches the items, if the applied TVA hallucinates, or if the Swiss UID violates the official `MOD11` checksum arithmetic.
* **Deterministic XML Parsers:** 100% LLM-free extraction of Swiss Bank `camt.053` statements for secure, structure-perfect transaction ingestion.
* **Cypher Reconciliation Engine:** A completely automated module running purely on Graph Mathematics that calculates precision deltas (`abs(invoice.amount - abs(tx.amount))`) to automatically match (`MATCHED_TO`) Invoices against Payments.
* **Swiss nFADP Compliant:** Operates on absolute data sovereignty, pointing exclusively to Europe-West endpoints.
* **W3C WebMCP Interceptor:** Designed to be audited by other AI agents securely via the unified Context Protocol.

---

## ⚙️ Technical Stack

* **Graph Database:** Neo4j (Cypher) for absolute schema retention, temporal tracking, and exact mathematical reconciliation.
* **A.I. Engine:** Google `gemini-2.5-flash` natively integrated with forced JSON structured inference.
* **Validation:** Pydantic (Strict coercion and algorithmic audits).
* **Environment:** Python 3.12, Docker-Compose (hardened read-only volumes).

---

## 📦 Quickstart

Menir requires a dedicated **Neo4j AuraDB** (or a local Dockerized Neo4j 5.x) and a **Google Gemini API Key**.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LPCDC/Menir.git
   cd Menir
   ```

2. **Set up the Environment:**
   Create a `.env` file at the root:
   ```env
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_secure_password
   NEO4J_DB=neo4j

   GOOGLE_API_KEY=your_gemini_api_key
   MENIR_INVOICE_LIVE=true
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Kernel (Ontology Bootstrap):**
   ```bash
   python -c "from src.v3.meta_cognition import MenirOntologyManager; import os; MenirOntologyManager(os.getenv('NEO4J_URI'), (os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))).bootstrap_system_graph()"
   ```

5. **Start the Menir Async Engine:**
   ```bash
   # Will monitor the /Menir_Inbox directory and orchestrate bimodal pipelines.
   python src/v3/core/menir_runner.py
   ```

---

## 🛡️ License & Liability
This project is licensed under the MIT License. 
It is engineered primarily as B2B middleware. Any production deployment acting upon real financial data must undergo routine human-in-the-loop audits. The authors bear no fiduciary or legal liability over automated accounting decisions made by the engine.

<div align="center">
  <i>Forged with precision. Built for absolute data sovereignty.</i>
</div>
