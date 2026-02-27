# MENIR V3 Specification: "Honest Mode"
(Versão 3.5.0 - Final Frozen)

- Princípio: Sem Auditoria (Sheets) = Sem Sucesso (Archive).
- Idempotência: SHA-256 local + PROJECT_NAME.
- Recovery: Se Nó (:Document {sha256, project}) existe no Neo4j, pula IA e repara Sheets.
- Labels: Person, Organization, Location, Role, DocumentConcept, Project, Asset, Event, Obligation, Risk.
- Gatekeeper: Apenas .pdf. Texto < 50 chars vai para Quarantine.

## Status
- [x] **Execução V3.0**: 100% Concluída (2026-01-18)
  - Drive Sync & Archive
  - Gemini Flash Free Tier
  - Neo4j Auth Remediation
  - Audit Hard-Stop

## Roadmap
- [x] **V3.1 - Metadata Injection (Completed)**: Enriched graph with advanced metadata & Root Ontology.
- [x] **Horizon 1: Refinamento Tático (Robustez & Estabilidade)**
    - **Architecture Hardening**:
        - **Type Safety**: Implemented `Pydantic` models for all Neo4j Nodes.
        - **Resilience**: Standardized `tenacity` retry logic across Middlewares.
        - **CI/CD Hygiene**: Restored GitHub Actions and purged the repository of heavy binaries.
    - **Sanitization Gate**: Strict PII scrubbing and Tenant-isolation via `TenantAwareDriver`.

- [x] **Horizon 2: Cloud Native & Cognitive Speed (The Optimization)**
    - **Staged Ingestion Pipeline (4-Fases)**: JSONL -> Pydantic Validation -> `UNWIND` Cypher Batching -> SHA-256 Signatures.
    - **LangGraph Integration**: State-driven workflow base orchestrator established (`langgraph_orchestrator.py`).
    - **Idempotency**: All Cypher injection scripts migrated from `CREATE` to `MERGE` patterns.

- [x] **Horizon 3: Fronteira de Inovação (Inteligência Cognitiva Operacional)**
    - **Módulo GatoMia**: Audits structural graph shapes (e.g. cycles) for Fraud Rings (`forensic_auditor.py`).
    - **Módulo Livro Débora**: Transforms plots into `(:Scene)-[:NEXT_SCENE]->(:Scene)` Linked-Lists, blocking logic errors via TLA+ style backwards traversals.
    - **Módulo Otani**: Evaluates agnostic Building Geometries mathematically against building codes (SHACL).
    - **Observability e HITL**: RAGAS tracker with manual human-in-the-loop locks over high risk prompts.

---

## ROADMAP V4.0: THE OMNI-INGESTOR

**(Status: Planning / Architecture Phase)**

### 1. SUBSYSTEM: THE TRUTH ARBITER (Metadata & Hierarchy)
- **Problem:** "The Trojan Horse" (Conflict between file metadata and text content).
- **Theory:** "Trust Tiering" with **Sanitization Gate**.
- **Mechanism:** 
    - **Sanitization:** Metadata checks against a "Generic Blacklist" (e.g., "Microsoft User", "Admin"). Only specific names are trusted.
    - **Tiering:** `Blockchain` > `Digital Signature` > `Sanitized Metadata` > `OCR Text`. 
    - **Conflict:** When conflicts arise, create a `:Conflict` node for human arbitration.

### 2. SUBSYSTEM: ADAPTIVE ONTOLOGY (Structured Data Defense)
- **Problem:** "Tower of Babel" (Schema Drift in Excel/CSV sources).
- **Theory:** "Medallion Graph Layering".
- **Mechanism:** Ingest data in layers:
    - **Bronze Layer:** Raw data nodes exactly as they appear in the source.
    - **Silver Layer:** AI-mapped schema (using embeddings to map "Qty" to "Quantity").
    - **Gold Layer:** Curated, strict ontology for the final application.

### 3. SUBSYSTEM: THE LAZY AUDITOR PROTOCOL (Visual Defense)
- **Problem:** "The Mirage" (AI hallucinations) & "The Bill" (API Quotas).
- **Theory:** "Probabilistic Invocation".
- **Mechanism:** Default to Text/OCR (Low Cost).
    - **Trigger:** Vision AI is ONLY triggered if "Visual Anchors" (e.g., "Figure X", "See Chart") are detected in text AND OCR fails to parse.
    - **Validation:** If cost permits, cross-reference Narrative vs. Data. Otherwise, flag complex visuals as `:NeedsReview` with a link to the raw image.

### 4. SUBSYSTEM: TEMPORAL PROVENANCE (Web & Live Data Defense)
- **Problem:** "Ghost Ship" (Dead links and changing web content).
- **Theory:** "Snapshotting & TTL (Time-To-Live)".
- **Mechanism:** The Graph never indexes a raw URL as a source of truth. It indexes a `(:Snapshot {timestamp: T})`. Web nodes have an `expires_at` property. When expired, the crawler revisits. If content changed, a new version node is created and linked via `[:UPDATED_FROM]`, preserving historical truth.
