"""
Menir v3.5 Import Manager
Handles massive data ingestion with checkpointing using ImportBatch nodes.
"""

import logging
from typing import Any, List
from src.v3.menir_bridge import get_bridge
from src.v3.core.schemas.identity import TenantContext

logger = logging.getLogger("ImportManager")

class ImportManager:
    def __init__(self):
        self.bridge = get_bridge()

    async def start_batch(self, batch_id: str, description: str = ""):
        """Creates or retrieves an ImportBatch node."""
        tenant_id = TenantContext.get()
        if not tenant_id:
            raise RuntimeError("Operação fora de contexto galvânico")

        query = f"""
        MERGE (b:ImportBatch:`{tenant_id}` {{uid: $uid}})
        SET b.description = $desc,
            b.started_at = datetime(),
            b.status = 'IN_PROGRESS',
            b.project = $proj
        RETURN b
        """
        async with self.bridge.driver.session() as session:
            await session.run(query, uid=batch_id, desc=description, proj=tenant_id)

    async def get_batch_progress(self, batch_id: str) -> int:
        """Returns the last_processed_index for a batch."""
        tenant_id = TenantContext.get()
        query = f"MATCH (b:ImportBatch:`{tenant_id}` {{uid: $uid}}) RETURN b.last_processed_index as idx"
        async with self.bridge.driver.session() as session:
            result = await session.run(query, uid=batch_id)
            record = await result.single()
            return record["idx"] if record and record["idx"] is not None else -1

    async def update_batch_progress(self, batch_id: str, last_index: int):
        """Updates the last_processed_index."""
        tenant_id = TenantContext.get()
        query = f"""
        MATCH (b:ImportBatch:`{tenant_id}` {{uid: $uid}})
        SET b.last_processed_index = $idx,
            b.updated_at = datetime()
        """
        async with self.bridge.driver.session() as session:
            await session.run(query, uid=batch_id, idx=last_index)

    async def finalize_batch(self, batch_id: str):
        """Marks a batch as completed."""
        tenant_id = TenantContext.get()
        query = f"""
        MATCH (b:ImportBatch:`{tenant_id}` {{uid: $uid}})
        SET b.status = 'COMPLETED',
            b.completed_at = datetime()
        """
        async with self.bridge.driver.session() as session:
            await session.run(query, uid=batch_id)

    def get_retransmit_query(self, tenant_id: str) -> str:
        """
        Returns the canonical retransmission Cypher.
        Requirement: WHERE cliente.index > b.last_processed_index
        """
        return f"""
        MATCH (b:ImportBatch:`{tenant_id}` {{uid: $batch_id}})
        MATCH (cliente:Client:`{tenant_id}`)
        WHERE cliente.index > b.last_processed_index
        RETURN cliente
        ORDER BY cliente.index ASC
        LIMIT $limit
        """
