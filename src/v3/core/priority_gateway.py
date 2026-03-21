"""
Menir v3.5 Priority Gateway
Implements a PriorityQueue for Neo4j queries to ensure SANTOS latency < 200ms.
"""

import asyncio
import logging
import time
from typing import Any, Callable, Coroutine
from dataclasses import dataclass, field

logger = logging.getLogger("PriorityGateway")

@dataclass(order=True)
class PrioritizedQuery:
    priority: int  # 0: Highest (SANTOS/Interactive), 1: Standard, 2: Batch (BECO)
    coro: Coroutine = field(compare=False)
    created_at: float = field(default_factory=time.time)

class PriorityGateway:
    def __init__(self, max_concurrency: int = 150):
        self.queue = asyncio.PriorityQueue()
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self._worker_task = None

    async def execute(self, priority: int, coro: Coroutine) -> Any:
        """Enqueues a query and waits for its result."""
        # Wrap the original coroutine to capture the result
        future = asyncio.get_event_loop().create_future()
        
        async def wrapped_coro():
            try:
                # yielding for batch operations
                if priority >= 2:
                    await asyncio.sleep(0.05)
                
                async with self.semaphore:
                    result = await coro
                    future.set_result(result)
            except Exception as e:
                if not future.done():
                    future.set_exception(e)

        item = PrioritizedQuery(priority=priority, coro=wrapped_coro())
        await self.queue.put(item)
        
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._process_queue())
            
        return await future

    async def _process_queue(self):
        """Standard consumer for the priority queue."""
        while not self.queue.empty():
            item = await self.queue.get()
            # In a real high-throughput system, we'd spawn multiple workers
            # but for Menir prioritization, we manage concurrency via the semaphore
            # inside the wrapped_coro.
            asyncio.create_task(item.coro)
            self.queue.task_done()

_gateway_instance: "PriorityGateway | None" = None

def get_gateway() -> PriorityGateway:
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = PriorityGateway(max_concurrency=150)
    return _gateway_instance
