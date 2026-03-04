from pydantic import BaseModel


class BaseNode(BaseModel):
    uid: str
    project: str  # tenant_id
    labels: list[str] = []


class Document(BaseNode):
    sha256: str
    name: str
    source: str | None = None
    labels: list[str] = ["Document"]


class Relationship(BaseModel):
    source_uid: str
    target_uid: str
    relation_type: str
    properties: dict = {}
