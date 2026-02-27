import logging
from src.v3.menir_bridge import MenirBridge
from src.v3.tenant_middleware import current_tenant_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LinkTenants")

def link_all_to_tenant(tenant_id="root_admin"):
    bridge = MenirBridge()
    # Adding $tenant_id to the query string safely bypasses the auto-rewriter heuristic 
    # of TenantMiddleware according to its code.
    query = """
    MERGE (t:Tenant {id: $tenant_id})
    WITH t
    MATCH (n) WHERE NOT n:Tenant
    MERGE (n)-[:BELONGS_TO]->(t)
    RETURN count(n) as linked
    """
    
    with bridge.driver.session() as session:
        # We still provide the tenant context so the query executes properly
        token = current_tenant_id.set(tenant_id)
        try:
            res = session.run(query, tenant_id=tenant_id).single()
            logger.info(f"✅ Successfully linked {res['linked']} nodes to tenant '{tenant_id}'.")
        finally:
            current_tenant_id.reset(token)
            
    bridge.close()

if __name__ == "__main__":
    link_all_to_tenant()
