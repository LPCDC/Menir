from pydantic import BaseModel, Field


class SystemPersonaPayload(BaseModel):
    """
    Strict validation for the System Persona extracted from the Graph
    before it initializes the LLM Context Window.
    """

    name: str = Field(..., min_length=2, description="The Persona designation (e.g. DEFAULT_MENIR)")
    version: str = Field(..., description="The semantic version of the Persona")
    system_prompt: str = Field(
        ..., min_length=20, description="The actual cognitive directive for the LLM"
    )


class Heartbeat(BaseModel):
    """
    System internal status check payload.
    """

    status: str
    uptime_seconds: int
    memory_usage_mb: float
