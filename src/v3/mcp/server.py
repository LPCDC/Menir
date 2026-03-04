"""
Menir MCP Server (Python)
Entry point for the Menir Model Context Protocol integration.
"""

import logging
import os
import sys

from dotenv import load_dotenv

# Ensure we are in the path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)

from mcp.server.fastmcp import FastMCP

from src.v3.mcp.protools import MenirTools

# Configure Logging (StdErr to not corrupt StdOut MCP transport)
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("MenirMCP")

# Load Config
load_dotenv()

# Security Override: Force usage of Reader User if available
# This ensures that even if the .env has 'neo4j' (admin), this process tries to use 'ai_reader'
# provided the user has set NEO4J_READER_PASSWORD or we fallback to the main one (with a warning).
reader_user = os.getenv("NEO4J_READER_USER", "ai_reader")
reader_pwd = os.getenv("NEO4J_READER_PASSWORD")

if reader_pwd:
    logger.info(f"🔒 Secure Mode: Using dedicated '{reader_user}' credentials.")
    os.environ["NEO4J_USER"] = reader_user
    os.environ["NEO4J_PASSWORD"] = reader_pwd
else:
    logger.warning(
        "⚠️  Security Warning: NEO4J_READER_PASSWORD not found. Using default credentials (potentially Admin)."
    )

# Initialize FastMCP
mcp = FastMCP("Menir Vital Graph")

# ==========================================
# Tool Registration
# ==========================================


@mcp.tool()
async def get_strict_schema() -> dict:
    """
    Returns the strict Graph Schema (Nodes & Relationships).
    Use this to understand the allowed ontology before querying.
    """
    return await MenirTools.get_strict_schema()


@mcp.tool()
async def search_logs(limit: int = 100, keyword: str | None = None) -> list[str]:
    """
    Reads the last N lines of the system log (menir.log).
    Useful for debugging errors or checking ingestion status.
    """
    # Simply delegate (Input validation handled by Pydantic in ProTools if we used the classes directly,
    # but FastMCP handles basic types. Validating ranges manually here or via helper)
    if limit > 200:
        limit = 200  # Enforce hard cap
    return await MenirTools.search_logs(limit, keyword)


@mcp.tool()
async def explain_node(uuid: str, show_pii: bool = False) -> dict:
    """
    Retrieves a Node and its immediate relationships (1-hop).
    Redacts PII unless 'show_pii' is True (which is logged).
    Returns JSON gracefully on timeout.
    """
    return await MenirTools.explain_node(uuid, show_pii)


@mcp.tool()
async def check_quarantine_reasons(days: int = 7) -> list[dict]:
    """
    Lists recent files that failed ingestion (Quarantine).
    Returns filename, hash, and error message.
    """
    return await MenirTools.check_quarantine_reasons(days)


if __name__ == "__main__":
    logger.info("🚀 Menir MCP Server Starting...")
    mcp.run()
