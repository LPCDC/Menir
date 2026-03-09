from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class PersonalEntity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    entity_type: Literal["Concept", "Theme", "Person", "Project", "Institution", "LifeEvent", "Insight", "Goal"] = Field(
        description="O tipo fundamental da entidade gerada."
    )
    name: str = Field(description="Nome do conceito ou entidade (Curto, objetivo).")
    description: str | None = Field(default=None, description="Descrição opcional ou contexto gerado pela IA sobre a entidade.")

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, v: str) -> str:
        """Sintaxe Camada 1: Normalização rigorosa em lowercase e strip para evitar duplicatas superficiais."""
        if isinstance(v, str):
            return v.strip().lower()
        return v

class PersonalRelationship(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    source_name: str = Field(description="Nome da entidade de origem exato como extraído em entities.")
    target_name: str = Field(description="Nome da entidade de destino exato como extraído em entities.")
    relation_type: Literal["INSPIRED_BY", "BECAME", "RELATED_TO", "PART_OF", "KNOWS", "PARTICIPATED_IN"] = Field(
        description="O verbo Cypher UPPERCASE que conecta os dois."
    )

class PersonalGraphPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    entities: list[PersonalEntity] = Field(description="Lista abrangente de conceitos e entidades pinçadas do insight pessoal.")
    relationships: list[PersonalRelationship] = Field(description="Lista de conexões formadas entre as entidades.")
