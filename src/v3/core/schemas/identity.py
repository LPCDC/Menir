import contextvars
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .base import BaseNode

# O Registro da Verdade para Isolamento Galvânico
ALLOWED_TENANTS = {"BECO", "SANTOS"}

# ContextVar for Zero-Trust Middleware (Galvanic Isolation)
TenantContext: contextvars.ContextVar[str | None] = contextvars.ContextVar("tenant_id", default=None)


class SecurityContextError(Exception):
    """Exceção levantada quando há tentativa de Violação de Isolamento Galvânico."""

    pass


class locked_tenant_context:
    """
    Context Manager que tranca o fluxo de execução assíncrona
    num Tenant específico (BECO ou SANTOS).
    Prevem que qualquer função filha altere o contexto furtivamente.
    """

    def __init__(self, tenant_id: str):
        if tenant_id not in ALLOWED_TENANTS:
            raise SecurityContextError(
                f"TENANT FORGERY: '{tenant_id}' não é um tenant reconhecido pelo Kernel."
            )
        self.target_tenant = tenant_id
        self.token: contextvars.Token[str | None] | None = None

    def __enter__(self):
        current_tenant = TenantContext.get()
        if current_tenant is not None and current_tenant != self.target_tenant:
            raise SecurityContextError(
                f"ISOLATION BREACH DETECTED: Tentativa de cross-talk. Contexto ativo é '{current_tenant}', interceptado payload para '{self.target_tenant}'."
            )
        self.token = TenantContext.set(self.target_tenant)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token:
            TenantContext.reset(self.token)


class Person(BaseNode):
    model_config = ConfigDict(extra="forbid")

    name: str
    email: str | None = None
    labels: list[str] = ["Person"]  # noqa: RUF012


class Organization(BaseNode):
    name: str
    labels: list[str] = ["Organization"]  # noqa: RUF012


class Tenant(BaseNode):
    """
    O Nó principal de Context Isolation.
    """

    name: Literal["BECO", "SANTOS"] = Field(
        description="A Enumeração rígida dos Tenants permitidos na arquitetura."
    )
    labels: list[str] = ["Tenant"]  # noqa: RUF012


class User(BaseNode):
    name: str = Field(description="O nome do Usuário.")
    email: str | None = Field(default=None)
    role: Literal["ADMIN", "AUDITOR", "USER"] = Field(default="USER")
    labels: list[str] = ["User", "Person"]  # noqa: RUF012


class Session(BaseModel):
    """
    Usado futuramente no JWT parsing para o Zero-Trust Middleware.
    """

    token: str
    tenant_id: Literal["BECO", "SANTOS"]
    user_id: str
    is_active: bool = True
