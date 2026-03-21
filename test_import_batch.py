import asyncio
import os
from src.v3.core.import_manager import ImportManager
from src.v3.core.schemas.identity import TenantContext
from src.v3.core.neo4j_pool import Neo4jPoolManager

async def test_import_batch():
    # Initialize Pool
    Neo4jPoolManager()
    
    im = ImportManager()
    batch_id = "test-batch-001"
    
    # Set Tenant
    TenantContext.set("BECO")
    
    print(f"--- Starting Batch: {batch_id} ---")
    await im.start_batch(batch_id, "Test Ingestion")
    
    initial_progress = await im.get_batch_progress(batch_id)
    print(f"Initial Progress: {initial_progress}")
    
    # Simulate partial progress
    print("Updating progress to 5...")
    await im.update_batch_progress(batch_id, 5)
    
    progress_after = await im.get_batch_progress(batch_id)
    print(f"Progress After Update: {progress_after}")
    assert progress_after == 5
    
    # Verify Cypher Predicate
    query = im.get_retransmit_query("BECO")
    print("Canonical Retransmit Query:")
    print(query)
    assert "WHERE cliente.index > b.last_processed_index" in query
    
    await im.finalize_batch(batch_id)
    print("Batch finalized.")

if __name__ == "__main__":
    asyncio.run(test_import_batch())
