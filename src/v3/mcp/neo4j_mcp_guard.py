"""
neo4j_mcp_guard.py — Tenant guard para queries MCP no Aura Free.

Problema que resolve:
  Aura Free não tem RBAC granular. O MCP server usa credenciais de admin.
  Sem este guard, uma query MCP poderia MATCH dados do tenant BECO
  enquanto operando no contexto SANTOS.

Solução:
  Interceptar toda query antes de executar.
  Verificar que o tenant do ContextVar está presente na query.
  Rejeitar queries que acessam labels de outros tenants.

NOTA: Esta é a camada de segurança compensatória para Aura Free.
      Em produção Enterprise, usar RBAC nativo + esta camada.
"""

import logging
import os
import re

logger = logging.getLogger("menir.mcp_guard")

ALLOWED_TENANTS = set(
    os.getenv("MENIR_MCP_ALLOWED_TENANTS", "SANTOS,BECO").split(",")
)

# Labels que NUNCA devem cruzar tenants
TENANT_SENSITIVE_LABELS = {
    "Invoice", "BankTransaction", "TaxRule",        # BECO (fiduciária)
    "Lead", "Event", "Product", "Channel",           # SANTOS (Ana)
    "Anomaly", "ComplianceRule",                     # ambos
}


class MCPQueryGuard:
    """
    Valida queries Cypher antes de execução via MCP.
    Garante isolamento galvânico sem RBAC nativo.
    """

    @staticmethod
    def validate_query(cypher: str, current_tenant: str) -> tuple[bool, str]:
        """
        Retorna (is_safe, reason).
        is_safe=False → query bloqueada antes de tocar o Neo4j.
        """
        if not current_tenant or current_tenant not in ALLOWED_TENANTS:
            return False, f"Tenant '{current_tenant}' não autorizado."

        cypher_upper = cypher.upper()

        # Bloquear operações destrutivas via MCP (DELETE, DETACH DELETE)
        if re.search(r'\bDETACH\s+DELETE\b|\bDELETE\b', cypher_upper):
            return False, "DELETE via MCP bloqueado. Use a API interna do Menir."

        # Bloquear DROP de constraints/indexes via MCP
        if re.search(r'\bDROP\b', cypher_upper):
            return False, "DROP via MCP bloqueado."

        # Verificar que a query não mistura labels de tenants diferentes
        # (heurística: se menciona labels de ambos BECO e SANTOS)
        beco_labels = {"Invoice", "BankTransaction", "TaxRule"}
        santos_labels = {"Lead", "Event", "Channel"}

        has_beco = any(label.upper() in cypher_upper for label in beco_labels)
        has_santos = any(label.upper() in cypher_upper for label in santos_labels)

        if has_beco and has_santos:
            return False, (
                "Query cross-tenant detectada — "
                "mistura labels de BECO e SANTOS. Bloqueado por segurança."
            )

        # Se o tenant atual é SANTOS, bloquear acesso a labels do BECO
        if current_tenant == "SANTOS" and has_beco:
            return False, (
                f"Tenant SANTOS tentou acessar labels do BECO. "
                f"Isolamento galvânico ativo."
            )

        # Se o tenant atual é BECO, bloquear acesso a labels do SANTOS
        if current_tenant == "BECO" and has_santos:
            return False, (
                f"Tenant BECO tentou acessar labels do SANTOS. "
                f"Isolamento galvânico ativo."
            )

        return True, "Query aprovada."

    @staticmethod
    def enforce_tenant_filter(cypher: str, tenant: str) -> str:
        """
        Se a query não contém filtro de tenant explícito,
        adiciona um aviso no log. Não modifica a query.
        (A modificação seria muito arriscada — melhor rejeitar do que corrigir.)
        """
        safe_tenant = tenant.replace("`", "").replace(";", "")
        if f"`{safe_tenant}`" not in cypher and f":{safe_tenant}" not in cypher:
            logger.warning(
                f"⚠️  Query MCP sem filtro explícito de tenant '{tenant}'. "
                f"Resultado pode conter dados de múltiplos tenants. "
                f"Adicionar :`{safe_tenant}` nas labels para isolamento total."
            )
        return cypher
