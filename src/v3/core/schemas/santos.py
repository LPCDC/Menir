from decimal import Decimal
from datetime import datetime
from pydantic import ConfigDict, Field
from .base import BaseNode

class SignalInput(BaseNode):
    """
    Schema de entrada para sinais cross-tenant.
    O peso (weight) deve estar entre 0.0 e 1.0.
    """
    model_config = ConfigDict(extra="forbid")
    
    signal_type: str
    weight: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
    description: str | None = None
    origin_tenant_hash: str
    # Campos de decay solicitados pelo arquiteto
    initial_score: Decimal = Decimal("1.0")
    decay_lambda: Decimal = Decimal("0.1")
    created_at: datetime = Field(default_factory=datetime.now)
    labels: list[str] = ["Signal"]

class InsightInput(BaseNode):
    """
    Schema de entrada para insights do grafo pessoal.
    """
    model_config = ConfigDict(extra="forbid")
    
    content: str
    decay_lambda: Decimal = Field(default=Decimal("0.05"))
    tags: list[str] = Field(default_factory=list)
    # Campos de decay solicitados pelo arquiteto
    initial_score: Decimal = Decimal("1.0")
    created_at: datetime = Field(default_factory=datetime.now)
    labels: list[str] = ["Insight"]

class DecisionHubEntry(BaseNode):
    """
    Nó centralizador de decisões. Gerado pelo sistema.
    """
    model_config = ConfigDict(extra="forbid")
    labels: list[str] = ["DecisionHub"]
