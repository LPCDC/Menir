"""
Menir Graph Schema (Source of Truth)
Defines allowed node types (Labels) and relationships for the Menir Ecosystem.
Used by MCP to prevent hallucinations.
"""

# Allowed Node Labels
LABELS = {
    "Project": "Root container for a knowledge domain",
    "Document": "Ingested file (PDF, TXT, MD)",
    "Chunk": "Vectorized text segment",
    "Person": "Human entity (Real or Fictional)",
    "Organization": "Company or Group",
    "Location": "Physical or Abstract Place",
    "Event": "Temporal occurrence",
    "Concept": "Abstract idea or topic"
}

# Allowed Relationships (Source Label -> Target Label)
RELATIONSHIPS = {
    "WROTE": ["Person -> Document"],
    "MENTIONS": ["Document -> Person", "Document -> Organization", "Document -> Location"],
    "BELONGS_TO": ["Chunk -> Document"],
    "HAS_CHUNK": ["Document -> Chunk"],
    "LOCATED_AT": ["Event -> Location", "Organization -> Location"],
    "PARTICIPATED_IN": ["Person -> Event"],
    "RELATED_TO": ["Concept -> Concept", "Person -> Person"],
    "MEMBER_OF": ["Person -> Organization"]
}

# Strict JSON Schema for MCP Tool
STRICT_SCHEMA = {
    "version": "1.0",
    "labels": LABELS,
    "relationships": RELATIONSHIPS
}
