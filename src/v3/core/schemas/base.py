from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    QUARANTINE = "quarantine"
    EXPORTED = "exported"


class BaseNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    uid: str
    project: str  # tenant_id
    labels: list[str] = []
    metadata: dict = Field(default_factory=dict, description="Dados não estruturados via LLM")


class Document(BaseNode):
    sha256: str
    name: str
    source: str | None = None
    status: DocumentStatus = DocumentStatus.PENDING
    labels: list[str] = ["Document"]


class Relationship(BaseModel):
    source_uid: str
    target_uid: str
    relation_type: str
    properties: dict = {}
