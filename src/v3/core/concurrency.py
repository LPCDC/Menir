import asyncio
import contextvars
import functools
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, TypeVar, Any

T = TypeVar("T")

logger = logging.getLogger("MenirConcurrency")
logger.setLevel(logging.INFO)

# pool definitions per MENIR_FASE47_ARCH.md
# cpu_pool: optimized for pyzbar, pypdfium2 (CPU-bound)
cpu_pool = ThreadPoolExecutor(max_workers=3, thread_name_prefix="MenirCPU")

# io_pool: optimized for Neo4j, filesystem (I/O-bound)
io_pool = ThreadPoolExecutor(max_workers=15, thread_name_prefix="MenirIO")

# MOMENTO 1 - Etapa 3: Semaphore to prevent PDF memory spikes on Synology NAS
pdf_mem_semaphore = asyncio.BoundedSemaphore(3)

async def run_in_custom_executor(
    executor: ThreadPoolExecutor, 
    func: Callable[..., T], 
    *args: Any, 
    **kwargs: Any
) -> T:
    """
    Runs a synchronous function in a custom executor with ContextVars propagation.
    This is the authorized replacement for asyncio.to_thread in Menir OS Phase 47.
    """
    loop = asyncio.get_running_loop()
    
    # contextvars.copy_context().run is required to propagate ContextVars 
    # (like TenantContext) across thread boundaries.
    ctx = contextvars.copy_context()
    
    # Create a partial to include kwargs (run_in_executor doesn't support them natively)
    partial_func = functools.partial(ctx.run, func, *args, **kwargs)
    
    return await loop.run_in_executor(executor, partial_func)

def shutdown_pools():
    """Graceful shutdown of concurrency pools."""
    logger.info("Shutting down Menir concurrency pools...")
    cpu_pool.shutdown(wait=True)
    io_pool.shutdown(wait=True)
