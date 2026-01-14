# Migration: Feature "normalize_chapter1_graph"

**Purpose**: Refactor existing Chapter 1 data in the graph to assign stable `entity_id` (slugs), enforce uniqueness, add provenance, and merge duplicates.

## Preconditions
1.  Backup existing database.
2.  Admin credentials in `.env`.

## Pseudocode / Logic
```python
# normalize_chapter1_graph.py
from neo4j import GraphDatabase
import unicodedata
import re

# Config
IMMUTABLE_ATTRS = {
    "Character": ["canonical_name", "birthdate", "gender"],
    "Place": ["canonical_name", "address"], 
}

def slugify(text):
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text

def main():
    # ... connection logic ...
    # 1. Create constraints
    # 2. Iterate nodes -> slugify -> merge (APOC)
    # 3. Add provenance
    # 4. Audit
```

## Cypher Snippets relative to Migration

### 1. Unique Constraints
```cypher
CREATE CONSTRAINT character_entity_id_unique IF NOT EXISTS FOR (c:Character) REQUIRE c.entity_id IS UNIQUE;
CREATE CONSTRAINT place_entity_id_unique IF NOT EXISTS FOR (p:Place) REQUIRE p.entity_id IS UNIQUE;
```

### 2. Merge Duplicate Characters
```cypher
MATCH (c:Character)
WHERE NOT exists(c.entity_id)
WITH c, apoc.text.slugify(c.name) AS slug
MERGE (canon:Character {entity_id: slug})
ON CREATE SET canon.name = c.name
WITH c, canon
CALL apoc.refactor.mergeNodes([c, canon], { properties: "combine", mergeRels: true })
YIELD node
RETURN node;
```

### 3. Audit
```cypher
MATCH (c1:Character), (c2:Character)
WHERE c1 <> c2 AND c1.entity_id = c2.entity_id
RETURN c1, c2;
```

### 4. Provenance
```cypher
MATCH (n)
WHERE (n:Character OR n:Place OR n:Scene OR n:Event) AND NOT exists(n.source_file)
SET n.source_file = "legacy_chapter1_import",
    n.proposal_id = "initial_migration",
    n.source_timestamp = datetime();
```
