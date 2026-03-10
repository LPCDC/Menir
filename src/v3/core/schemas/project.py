from pydantic import Field, ConfigDict, model_validator
from typing import Literal, Any
from .base import BaseNode

class Project(BaseNode):
    """
    Entidade Primária do Grafo pessoal (Gestão de Vida).
    """
    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Nome legível do projeto.")
    owner: str = Field(description="Entidade/Pessoa responsável (uid do User).")
    
    # original_intent is immutable after creation. Handled by the application logic, but marked here.
    original_intent: str = Field(description="A tese ou intenção fundadora do projeto. Imutável no grafo.")
    
    status: Literal["Active", "Paused", "Completed", "Archived", "Cancelled"] = Field(
        default="Active", description="Estado atual do projeto."
    )
    
    health_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Score calculado on-read com base no last_pulse_at, insights vinculados nos últimos 30 dias e documentos recentes."
    )
    
    created_at: str = Field(description="Timestamp ISO 8601 da criação do projeto.")
    last_pulse_at: str | None = Field(default=None, description="Timestamp ISO 8601 da última modificação ou insight vinculado.")

    labels: list[str] = ["Project"]

    # Relations proposed (handled in Cypher mostly):
    # (:User)-[:LEADS]->(:Project)
    # (:Project)-[:BELONGS_TO_TENANT]->(:Tenant)
    # (:Document)-[:ATTACHED_TO]->(:Project)
    # (:Insight)-[:ADVANCES]->(:Project)
    # (:Project)-[:SPAWNED_INSIGHT]->(:Insight)
    # (:Collaborator)-[:CONTRIBUTES_TO]->(:Project)
