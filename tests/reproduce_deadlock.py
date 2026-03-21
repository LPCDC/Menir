import asyncio
import aiohttp
import pytest
import os
from dotenv import load_dotenv

load_dotenv()

JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRfaWQiOiJCRUNPIiwidXNlcl91aWQiOiJ0ZXN0LXVzZXIiLCJpYXQiOjE3NzQwNjY4MTYsImV4cCI6MTc3NDA3MDQxNn0.6fsWkSK-VWHXb-KRNcBYPOhjUxMsrmF3X33YiJBobTnY"
API_URL = "http://localhost:8080/api/v3/quarantine/documents"

async def fire_request(session, i):
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
    try:
        async with session.get(API_URL, headers=headers, timeout=10) as resp:
            status = resp.status
            return status
    except asyncio.TimeoutError:
        return "TIMEOUT"
    except Exception as e:
        return str(e)

@pytest.mark.asyncio
async def test_reproduce_deadlock():
    """
    Saturates the pool by firing many concurrent requests to a handler 
    that uses the synchronous driver session.
    """
    # Note: This test assumes the server is RUNNING.
    # In a real CI, we would start the server here.
    
    async with aiohttp.ClientSession() as session:
        # Fire 60 requests (Pool limit is 50)
        tasks = [fire_request(session, i) for i in range(60)]
        results = await asyncio.gather(*tasks)
        
        timeouts = [r for r in results if r == "TIMEOUT"]
        errors = [r for r in results if isinstance(r, str) and r != "TIMEOUT" and not str(r).isdigit()]
        
        print(f"\nResults: {results}")
        print(f"Timeouts detected: {len(timeouts)}")
        
        # If the deadlock is real, we expect many timeouts because the sync sessions 
        # block the worker threads while waiting for the async pool to release connections
        # that are stuck behind the very threads they are waiting for.
        assert len(timeouts) > 0, "Deadlock not reproduced: No timeouts detected under saturation."

if __name__ == "__main__":
    asyncio.run(test_reproduce_deadlock())
