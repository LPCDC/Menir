from typing import Optional, Dict, Any, Literal
from datetime import datetime, timezone
import uuid
import re
from pydantic import BaseModel, Field, field_validator, ConfigDict

# ==========================================
# CORE PRIMITIVES
# ==========================================

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class BaseNode(BaseModel):
    """
    Base Model for all Graph Nodes.
    Enforces audit fields and unique identifiers.
    """
    uid: str = Field(default_factory=generate_uuid, description="Unique Node ID")
    created_at: str = Field(default_factory=utc_now_iso, description="ISO 8601 Timestamp")
    project: str = Field(..., min_length=1, description="Project Context (e.g. 'Menir')")
    labels: list[str] = Field(default_factory=list, description="Neo4j Labels")

    model_config = ConfigDict(extra="ignore") 

# ==========================================
# ENTITY MODELS
# ==========================================

class Person(BaseNode):
    """
    Represents a Human Being (Real or Fictional).
    """
    name: str = Field(..., min_length=2, description="Full Name")
    role: Optional[str] = Field(None, description="Role or Title")
    is_real: bool = Field(False, description="True if part of Root Ontology (Real World)")
    context: Optional[str] = Field(None, description="Narrative Context or 'Real World'")

    def __init__(self, **data):
        super().__init__(**data)
        if "Person" not in self.labels:
            self.labels.append("Person")
        if self.is_real and "Root" not in self.labels:
             self.labels.append("Root")

    @field_validator('name')
    @classmethod
    def name_must_be_capitalized(cls, v: str) -> str:
        if not v[0].isupper():
            raise ValueError('Name must start with a capital letter')
        return v.strip()

class Organization(BaseNode):
    """
    Represents a Company, NGO, or Group.
    """
    name: str = Field(..., min_length=2)
    industry: Optional[str] = Field(None)

    def __init__(self, **data):
        super().__init__(**data)
        if "Organization" not in self.labels:
            self.labels.append("Organization")

class Document(BaseNode):
    """
    Represents an Ingested File (PDF/Text).
    """
    filename: str = Field(..., min_length=3)
    sha256: str = Field(..., pattern=r"^[a-fA-F0-9]{64}$", description="SHA-256 Hash")
    status: Literal['processed', 'archived', 'quarantine'] = 'processed'

    def __init__(self, **data):
        super().__init__(**data)
        if "Document" not in self.labels:
             self.labels.append("Document")

class GenericNode(BaseNode):
    """
    Fallback for Location, Event, etc.
    """
    name: str = Field(..., min_length=1)

# ==========================================
# RELATIONSHIP MODEL
# ==========================================

class Relationship(BaseModel):
    """
    Represents a Graph Edge.
    """
    source_uid: str
    target_uid: str
    relation_type: str = Field(..., pattern=r"^[A-Z_]+$", description="UPPER_SNAKE_CASE Type")
    properties: Dict[str, Any] = Field(default_factory=dict)

    @field_validator('relation_type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        return v.upper()
