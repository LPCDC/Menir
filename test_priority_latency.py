import asyncio
import time
import os
from src.v3.core.priority_gateway import get_gateway

async def heavy_batch_op(i):
    # Simulate a "Neo4j" query with some artificial delay
    await asyncio.sleep(0.1)
    return f"Batch-{i}"

async def interactive_query():
    # Simulate an interactive query
    await asyncio.sleep(0.01)
    return "Interactive-SANTOS"

async def run_benchmark():
    gateway = get_gateway()
    
    print("--- Starting Priority Benchmark ---")
    
    # 1. Start heavy batch (Priority 2)
    batch_tasks = []
    print("Enqueuing 20 heavy batch tasks (Priority 2)...")
    for i in range(20):
        batch_tasks.append(gateway.execute(priority=2, coro=heavy_batch_op(i)))
    
    # Wait a bit to ensure they are in queue
    await asyncio.sleep(0.05)
    
    # 2. Fire high-priority interactive query (Priority 0)
    print("Firing High-Priority Interactive Query (Priority 0)...")
    start_time = time.time()
    interactive_res = await gateway.execute(priority=0, coro=interactive_query())
    latency = (time.time() - start_time) * 1000
    
    print(f"Interactive Result: {interactive_res}")
    print(f"LATENCY: {latency:.2f}ms")
    
    assert latency < 200, f"Latency {latency}ms exceeded 200ms target!"
    print("✅ LATENCY WITHIN TARGET (< 200ms)")
    
    # Cleanup batch tasks
    await asyncio.gather(*batch_tasks)
    print("Batch tasks completed.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
