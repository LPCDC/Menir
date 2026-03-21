import asyncio
import os
import psutil
import logging
import sys
from concurrent.futures import ThreadPoolExecutor

# Force path to find src.v3
sys.path.append(os.getcwd())

from src.v3.skills.qr_extractor import extract_qr_from_pdf
from src.v3.core.concurrency import pdf_mem_semaphore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MemTest")

async def monitor_memory(stop_event):
    process = psutil.Process(os.getpid())
    max_mem = 0
    while not stop_event.is_set():
        current_mem = process.memory_info().rss / (1024 * 1024)  # MB
        if current_mem > max_mem:
            max_mem = current_mem
        await asyncio.sleep(0.1)
    return max_mem

async def run_test():
    file_path = r"tests/fixtures/real/02032026_Amorim dos Santos Glayce.pdf"
    if not os.path.exists(file_path):
        logger.error(f"Fixture not found at: {file_path}")
        return
    logger.info(f"Using fixture: {file_path}")

    stop_event = asyncio.Event()
    monitor_task = asyncio.create_task(monitor_memory(stop_event))

    logger.info("Starting PDF processing...")
    initial_mem = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    
    # Run 5 extractions in parallel to test semaphore (BoundedSemaphore(3))
    tasks = [extract_qr_from_pdf(file_path) for _ in range(5)]
    results = await asyncio.gather(*tasks)
    
    stop_event.set()
    max_mem = await monitor_task
    final_mem = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)

    logger.info(f"Initial Memory: {initial_mem:.2f} MB")
    logger.info(f"Peak Memory: {max_mem:.2f} MB")
    logger.info(f"Final Memory (post-cleanup): {final_mem:.2f} MB")
    logger.info(f"Extraction Results: {len([r for r in results if r])} successes out of 5")

if __name__ == "__main__":
    asyncio.run(run_test())
