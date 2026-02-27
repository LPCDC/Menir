import re
import logging
from neo4j import GraphDatabase
import contextvars

logger = logging.getLogger("TenantMiddleware")

class SecurityViolationError(Exception):
    """Raised when a query is attempted without a valid Tenant context."""
    pass

# Context variable securely tracks the tenant_id in async/concurrent LangGraph flows
current_tenant_id = contextvars.ContextVar("current_tenant_id", default=None)

class TenantAwareSession:
    """Wrapper around neo4j.Session to enforce tenant isolation."""
    def __init__(self, session):
        self._session = session

    def run(self, query, **kwargs):
        tenant_id = current_tenant_id.get()
        if not tenant_id:
            logger.critical("Security Violation: Attempted DB access without tenant_id")
            raise SecurityViolationError("FATAL: No tenant_id provided for DB transaction. Cross-tenant leakage prevented.")
        
        rewritten_query = self._rewrite_query(query)
        kwargs['tenant_id'] = tenant_id
        
        if rewritten_query != query:
            logger.debug(f"AST Sandboxing: Rewrote query to enforce tenant '{tenant_id}'")
            
        return self._session.run(rewritten_query, **kwargs)

    def _rewrite_query(self, query: str) -> str:
        """
        Regex-based Cypher rewriting (Sandboxing) to automatically inject:
        -[:BELONGS_TO]->(t:Tenant {id: $tenant_id})
        """
        # If the query already handles tenant or is a basic administration query, skip
        if "t:Tenant" in query or "$tenant_id" in query or "CREATE CONSTRAINT" in query or "CREATE INDEX" in query or "CALL db" in query:
            return query
            
        rewritten = query
        
        # Heuristic: Extract the primary node variable from the first MATCH statement
        var_match = re.search(r"MATCH\s*\(\s*([a-zA-Z0-9_]+)\s*[:\)\{]", rewritten, re.IGNORECASE)
        
        if var_match:
            var_name = var_match.group(1)
            tenant_clause = f" WHERE ({var_name})-[:BELONGS_TO]->(:Tenant {{id: $tenant_id}}) "
            
            if re.search(r"WHERE", rewritten, re.IGNORECASE):
                rewritten = re.sub(r"(?i)WHERE", tenant_clause + "AND ", rewritten, count=1)
            elif re.search(r"RETURN", rewritten, re.IGNORECASE):
                rewritten = re.sub(r"(?i)RETURN", tenant_clause + "RETURN ", rewritten, count=1)
            elif re.search(r"WITH", rewritten, re.IGNORECASE):
                rewritten = re.sub(r"(?i)WITH", tenant_clause + "WITH ", rewritten, count=1)
            elif re.search(r"SET", rewritten, re.IGNORECASE):
                rewritten = re.sub(r"(?i)SET", tenant_clause + "SET ", rewritten, count=1)
            else:
                rewritten += tenant_clause
                
        return rewritten

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

class TenantAwareDriver:
    """Wrapper over Neo4j Driver to yield TenantAwareSessions.
    
    Automatically injects database= into every session so AuraDB
    sessions always target the correct database without per-call config.
    """
    def __init__(self, driver, db: str = "neo4j"):
        self._driver = driver
        self._db = db
        
    def session(self, **kwargs):
        # Inject the target database unless the caller explicitly overrides it
        kwargs.setdefault("database", self._db)
        session = self._driver.session(**kwargs)
        return TenantAwareSession(session)
        
    def close(self):
        self._driver.close()
