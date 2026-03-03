"""
Menir V3 - Pydantic Domain Models (Ontology Schema)
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class BaseNode(BaseModel):
    uid: str
    project: str  # tenant_id
    labels: List[str] = []

class Person(BaseNode):
    name: str
    email: Optional[str] = None
    labels: List[str] = ["Person"]

class Organization(BaseNode):
    name: str
    labels: List[str] = ["Organization"]

class Document(BaseNode):
    sha256: str
    name: str
    source: Optional[str] = None
    labels: List[str] = ["Document"]

class Relationship(BaseModel):
    source_uid: str
    target_uid: str
    relation_type: str
    properties: dict = {}
