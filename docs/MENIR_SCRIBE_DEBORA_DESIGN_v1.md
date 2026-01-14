# Menir Scribe Design Doc: Livro Débora (v1)

## Context
This document defines the design for "Scribe v1", a subsystem responsible for ingesting narrative content (PDFs of "Livro Débora") into the Menir Knowledge Graph. 
The core principle is **Safety First**: Scribe DOES NOT write to Neo4j. It generates **Proposals** (JSONL) that must be applied by a separate, governed process (or human review).

## 1. Ontology: Livro Débora
The ontology focuses on representing a literary work, its structure, and its extracted entities.

### Node Types
| Node Label | Key Properties | Description |
| :--- | :--- | :--- |
| **Project** | `project_id`="livro_debora", `type`="narrative" | The container for this initiative. |
| **Work** | `work_id`="debora_main", `title`, `version` | The specific book or narrative work. |
| **Chapter** | `chapter_id`, `index` (int), `title` | A division of the work. |
| **Fragment** | `fragment_id` (hash), `text`, `order` (int) | A granular piece of text (scene or paragraph). |
| **Character** | `character_id`, `name`, `role` | A fictional character in the story. |
| **RealPerson** | `person_id`, `label_public`, `sensitivity` | A real person the character is based on. |
| **Place** | `place_id`, `name`, `city`, `type` | A location in the story. |
| **TimeRef** | `time_id`, `label`, `granularity` | A temporal reference (e.g., "morning", "autumn 2019"). |
| **Theme** | `theme_id`, `label` | A thematic element found in a fragment. |

### Relationships
- `(:Project)-[:FOCUSES_ON]->(:Work)`
- `(:Work)-[:HAS_CHAPTER]->(:Chapter)`
- `(:Chapter)-[:HAS_FRAGMENT]->(:Fragment)`
- `(:Fragment)-[:MENTIONS_CHARACTER]->(:Character)`
- `(:Fragment)-[:SET_IN]->(:Place)`
- `(:Fragment)-[:HAS_TIME_REF]->(:TimeRef)`
- `(:Fragment)-[:EXPLORES_THEME]->(:Theme)`
- `(:Character)-[:BASED_ON {strength: float}]->(:RealPerson)`

## 2. Pipeline Architecture
The Scribe pipeline runs locally via `menir_cli.py`.

### Inputs
- Source: `artifacts/debora/*.pdf`
- Naming convention: `BETTER_IN_MANHATTAN_CAP<N>.pdf`

### Process Steps
1.  **PDF Loader**: Reads text from PDF.
2.  **Fragmenter**: Splits text into logical chunks (Paragraphs or Scenes). 
    *   *Strategy v1*: Split by double line breaks or specific delimiters.
3.  **Extractor (NLP/Regex/LLM)**: 
    *   Identifies Entities (Characters, Places).
    *   For v1, we may use simple regex or keyword matching, or a placeholder for LLM extraction.
4.  **Proposal Builder**: 
    *   Constructs a Graph Proposal object.
    *   Hashes content to generate deterministic IDs (`fragment_id`).

### Output: Proposal JSONL
File: `data/proposals/debora_scribe_v1.jsonl`

Format:
```json
{
  "proposal_id": "uuid",
  "project_id": "livro_debora",
  "timestamp": "iso8601",
  "nodes": [
    {"id": "debora_main", "labels": ["Work"], "properties": {...}},
    {"id": "frag_hash_123", "labels": ["Fragment"], "properties": {...}}
  ],
  "relationships": [
    {"source": "debora_main", "target": "chap_1", "type": "HAS_CHAPTER", "properties": {}}
  ]
}
```

## 3. Governance
- **Canonical Logs**: All Scribe executions are logged to `data/operations.jsonl` with `action="scribe_proposal"`.
- **Idempotency**: `fragment_id` generation must be deterministic (hash of content + indices) to avoid dupes if run multiple times.
- **Review**: The User (or specific Reviewer Agent) reviews the JSONL before any `ingest` command is run (Ingester is out of scope for this task, but the data shape must be ready).

## 4. CLI Interface
Command: `python scripts/menir_cli.py scribe-debora`
- Scans `artifacts/debora/`
- Runs pipeline
- Outputs stats to console: "Generated X fragments, Y characters."
