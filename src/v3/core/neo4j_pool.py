"""
Menir Core V5.1 - Unified Neo4j Connection Pool
A thread-safe singleton managing the primary Neo4j Driver.
Prevents "Write-Lock Saturation" caused by multiple module instantiations.
"""

import logging
import os
import atexit
from threading import Lock
from typing import Optional

from neo4j import AsyncGraphDatabase, AsyncDriver

logger = logging.getLogger("Neo4jPool")

class Neo4jPoolManager:
    _instance: Optional["Neo4jPoolManager"] = None
    _lock: Lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Neo4jPoolManager, cls).__new__(cls)
                cls._instance._init_driver()
            return cls._instance

    def _init_driver(self):
        from dotenv import load_dotenv
        load_dotenv(override=True)

        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD") or os.getenv("NEO4J_PWD")

        if not password:
            logger.warning("NEO4J_PASSWORD is not set. Database connections will fail.")

        self.driver: AsyncDriver = AsyncGraphDatabase.driver(
            uri, 
            auth=(user, password),
            max_connection_lifetime=3600,
            max_connection_pool_size=50,
            connection_acquisition_timeout=60.0
        )
        # Async verify_connectivity in a separate thread if needed, or skip for bootstrap
        # In this singleton _init, we can't easily await.
        # We will verify on first use or use a simplified check.
        logger.info("✅ Unified Neo4j AsyncDriver Instance created.")

    def get_driver(self) -> AsyncDriver:
        return self.driver

    async def close(self):
        if hasattr(self, "driver") and self.driver:
            await self.driver.close()
            logger.info("🔌 Unified Neo4j AsyncDriver Instance closed.")

# Ensure graceful shutdown
@atexit.register
def shutdown_pool():
    if Neo4jPoolManager._instance:
        Neo4jPoolManager._instance.close()

def get_shared_driver() -> AsyncDriver:
    """Helper method to access the unified driver."""
    return Neo4jPoolManager().get_driver()
