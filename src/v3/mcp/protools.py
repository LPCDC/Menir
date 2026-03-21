"""
Menir MCP Professional Tools
Implements the core observational capabilities for the Agent.
"""

import asyncio
import logging
import os
from typing import Any

from src.v3.graph_schema import STRICT_SCHEMA
from src.v3.mcp.security import PiiFilter
from src.v3.menir_bridge import MenirBridge, get_bridge
from src.v3.core.concurrency import run_in_custom_executor, io_pool

# Initialize Helper Logger
logger = logging.getLogger("MenirMCPTools")

# ==========================================
# Tool Logic
# ==========================================


class MenirTools:
    def __init__(self):
        # We initialize Bridge lazily or per-request to avoid keeping connections open?
        # Better to have a singleton bridge for the Server process.
        pass

    @staticmethod
    async def get_strict_schema() -> dict[str, Any]:
        """Returns the official Graph Schema for Menir."""
        from typing import cast
        return cast(dict[str, Any], STRICT_SCHEMA)

    @staticmethod
    async def search_logs(limit: int = 100, keyword: str | None = None) -> list[str]:
        """
        Reads the last N lines of menir.log.
        Applies horizontal truncation (>500 chars) and PII redaction.
        """
        log_path = os.path.join(os.getcwd(), "logs", "menir.log")
        if not os.path.exists(log_path):
            return ["Log file not found."]

        results = []
        try:
            # Efficient tailing for large files is complex in pure Python without deps,
            # but usually reading lines and taking last N is fine for <100MB logs.
            with open(log_path, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            # Filter first
            if keyword:
                lines = [l for l in lines if keyword.lower() in l.lower()]  # noqa: E741

            # Slice last N
            last_lines = lines[-limit:]

            for line in last_lines:
                # 1. PII Redaction
                clean_line = PiiFilter.redact_log_line(line)

                # 2. Horizontal Truncation
                if len(clean_line) > 500:
                    clean_line = clean_line[:500] + "...[TRUNCATED]"

                results.append(clean_line.strip())

            return results
        except Exception as e:
            return [f"Error reading logs: {e!s}"]

    @staticmethod
    async def explain_node(uuid: str, show_pii: bool = False) -> dict[str, Any]:
        """
        Fetches Node properties + 1-Hop Relationships with 5s Timeout.
        """
        bridge = get_bridge()  # Assuming Env Vars are set
        try:
            # Enforce 5s Timeout on Neo4j Operation
            async def _fetch():
                # Note: MenirBridge is sync, so we wrap it or use it directly.
                # Since we are in an async function, we can run it in an executor if needed,
                # but for simplicity we rely on the bridge's internal speed.
                # However, to strictly enforce timeout at Python level:
                return await run_in_custom_executor(io_pool, _get_node_data, bridge, uuid)

            data = await asyncio.wait_for(_fetch(), timeout=5.0)

            # Redact PII
            if not show_pii:
                data["properties"] = PiiFilter.redact_node(data.get("properties", {}))

            from typing import cast
            return cast(dict[str, Any], data)

        except TimeoutError:
            return {"error": "Database timeout (5s)", "status": "offline"}
        except Exception as e:
            return {"error": f"Database Error: {e!s}", "status": "error"}

    @staticmethod
    async def check_quarantine_reasons(days: int = 7) -> list[dict]:
        """
        Analyzes nodes in 'quarantine' status.
        """
        bridge = MenirBridge()
        from src.v3.core.schemas.base import DocumentStatus
        query = f"""
        MATCH (n:Document {{status: '{DocumentStatus.QUARANTINE.value}'}})
        WHERE n.ingested_at >= datetime() - duration({days: $days})
        RETURN n.filename as file, n.sha256 as hash, n.error_msg as error
        LIMIT 50
        """
        try:

            async def _run_query():
                with bridge.driver.session() as session:
                    result = session.run(query, days=days)
                    return [
                        {"file": r["file"], "hash": r["hash"], "error": r.get("error", "Unknown")}
                        for r in result
                    ]

            return await asyncio.wait_for(_run_query(), timeout=5.0)

        except TimeoutError:
            return [{"error": "Database timeout checking quarantine"}]
        except Exception as e:
            return [{"error": str(e)}]

    @staticmethod
    async def query_memory(tenant_id: str, cypher_query: str) -> list[dict]:
        """
        Substitui o antigo talk.py. Permite que Agentes WebMCP façam queries
        diretas no grafo, garantindo que operações destrutivas sejam bloqueadas,
        a menos que o Agente seja altamente privilegiado.
        """
        if not tenant_id:
            raise ValueError("Tenant_ID é obrigatório para query_memory.")

        upper_query = cypher_query.upper()
        # Fast-fail safety against destructive queries in standard layer
        destructive_keywords = ["DELETE", "DETACH", "REMOVE", "DROP", "CREATE INDEX"]
        if tenant_id != "ROOT" and any(k in upper_query for k in destructive_keywords):
            raise PermissionError(
                f"Isolamento: O Tenant {tenant_id} não tem permissão para queries destrutivas via MCP."
            )

        def _run():
            bridge = get_bridge()
            with bridge.driver.session() as session:
                # Na v6.0 introduziremos Neo4j Role-Based Access Control por Tenant real.
                result = session.run(cypher_query)
                return [record.data() for record in result]

        try:
            return await run_in_custom_executor(io_pool, _run)
        except Exception as e:
            logger.exception("Falha ao executar query_memory via MCP.")
            return [{"error": str(e)}]


# Internal Helper for Explain Node
def _get_node_data(bridge, uuid):
    with bridge.driver.session() as session:
        # 1. Fetch Node
        node_q = "MATCH (n {uid: $uid}) RETURN labels(n) as labels, properties(n) as props"
        node_res = session.run(node_q, uid=uuid).single()

        if not node_res:
            return {"error": "Node not found"}

        # 2. Fetch 1-Hop Rels (Incoming & Outgoing)
        # Limit to 20 rels to avoid massive dumps
        rel_q = """
        MATCH (n {uid: $uid})-[r]-(target)
        RETURN type(r) as type, startNode(r) = n as is_start, labels(target) as other_labels, target.name as other_name, target.uid as other_uid
        LIMIT 20
        """
        rel_res = session.run(rel_q, uid=uuid)

        relationships = []
        for r in rel_res:
            direction = "OUT" if r["is_start"] else "IN"
            relationships.append(
                {
                    "type": r["type"],
                    "direction": direction,
                    "target_label": r["other_labels"][0] if r["other_labels"] else "Unknown",
                    "target_name": r["other_name"] or "Unnamed",
                    "target_uid": r["other_uid"],
                }
            )

        return {
            "uid": uuid,
            "labels": node_res["labels"],
            "properties": node_res["props"],
            "relationships": relationships,
        }
