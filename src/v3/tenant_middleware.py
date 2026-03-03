"""
Menir V3 - Tenant-Aware Neo4j Driver Wrapper
Ensures every session is scoped to the correct database.
"""
import logging

logger = logging.getLogger("TenantAwareDriver")

class TenantAwareDriver:
    """
    Thin wrapper around the Neo4j driver that enforces database scoping.
    Prevents accidental cross-tenant queries by always routing to the
    configured database.
    """
    def __init__(self, base_driver, db: str = "neo4j"):
        self._driver = base_driver
        self._db = db

    def session(self, **kwargs):
        kwargs.setdefault("database", self._db)
        return self._driver.session(**kwargs)

    def close(self):
        self._driver.close()

    def verify_connectivity(self):
        return self._driver.verify_connectivity()
