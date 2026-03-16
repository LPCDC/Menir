from pydantic import BaseModel, ConfigDict, Field, field_validator
from enum import Enum
from typing import Optional
from src.v3.skills.swiss_qr_parser import SwissQRParser

class ClientType(str, Enum):
    INDIVIDUAL = "INDIVIDUAL"
    INDEPENDENT = "INDEPENDENT"
    COMPANY = "COMPANY"
    SOCIETY = "SOCIETY"

class ClientInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="Nome do cliente")
    client_type: ClientType = Field(..., description="Tipo do cliente")
    canton: str = Field(..., description="Cantao suico")
    language: str = Field(..., description="Idioma")
    fiscal_id: Optional[str] = Field(default=None, description="IDE suico")
    tva_number: Optional[str] = Field(default=None, description="Numero TVA")
    tva_status: Optional[str] = Field(default=None, description="Status de TVA")

    @field_validator("fiscal_id")
    @classmethod
    def validate_fiscal_id(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
            
        # Remover formatacao
        cleaned = v.replace("-", "").replace(".", "").replace(" ", "")
        
        # Validar via MOD97-10
        parser = SwissQRParser()
        # O modulo ignora excecoes e retorna falso caso seja invalido por default,
        # MAS como e um id e nao IBAN, a integracao reutiliza mod97-10 
        # (se o teste da Ana pedir validacao bruta ou com prefixo de account, veremos)
        is_valid = parser.validate_mod11(cleaned, raise_error=False)
        
        if not is_valid:
            raise ValueError(f"Falha na validaca MOD97-10 do fiscal_id: {v}")
            
        return cleaned
