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
    origin: str = "UPLOAD"  # EMAIL, WHATSAPP, UPLOAD, SCAN, FOLDER_WATCHER
    status: DocumentStatus = DocumentStatus.PENDING
    labels: list[str] = ["Document"]


class QuarantineItem(BaseNode):
    name: str
    file_hash: str
    reason: str
    quarantined_at: str = Field(description="ISO timestamp")
    status: str = "PENDING"
    origin: str = "UPLOAD"
    document_type: str | None = None
    confidence: float | None = None
    language: str | None = None
    labels: list[str] = ["QuarantineItem"]


class Relationship(BaseModel):
    source_uid: str
    target_uid: str
    relation_type: str
    properties: dict = {}
