from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
from src.v3.core.schemas.base import BaseNode

class PersonNode(BaseNode):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(description="Name of the person")
    nicknames: list[str] = Field(default_factory=list, description="Other known names or aliases")
    role_or_context: str = Field(default="", description="The context where this person is known")
    trust_score: float = Field(default=0.5, description="On-Read fallback trust score")
    is_virtual: bool = Field(default=False, description="True if this is a cross-tenant reference node")
    referenced_uid: Optional[str] = Field(default=None, description="The real node UID in the target tenant")
    referenced_tenant: Optional[str] = Field(default=None, description="The target tenant (e.g. BECO) if virtual")

class ProjectNode(BaseNode):
    model_config = ConfigDict(extra="forbid")
    name: str
    description: str = ""
    status: Literal['active', 'completed', 'paused'] = 'active'
    
class LifeEventNode(BaseNode):
    model_config = ConfigDict(extra="forbid")
    title: str
    date: str = ""
    impact_level: int = 1

class InsightNode(BaseNode):
    model_config = ConfigDict(extra="forbid")
    content: str
    tags: list[str] = Field(default_factory=list)
    source_context: str = ""

class GoalNode(BaseNode):
    model_config = ConfigDict(extra="forbid")
    title: str
    deadline: Optional[str] = None
    status: Literal['active', 'reached'] = 'active'

class CapturePayload(BaseModel):
    
    entity_type: Literal["Person", "Project", "LifeEvent", "Insight", "Goal"]
    name_or_title: str = Field(description="The primary name or title extracted")
    context: str = Field(description="Contextual information to distinguish this entity")
    impact_score: int = Field(description="1 to 10 score indicating how important this entity is in the text")

class CaptureResponse(BaseModel):
    entities: list[CapturePayload] = Field(description="List of extracted entities")
