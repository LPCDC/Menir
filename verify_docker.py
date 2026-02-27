
"""
Menir Internal Probe (verify_docker.py)
Checks connectivity and environment health before starting the main Runner.
Acts as a "Canary" for the Docker container.
"""
import os
import sys
import logging
import google.generativeai as genai
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Configure minimal logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [PROBE] - %(message)s')
logger = logging.getLogger("Probe")

def check_env_vars():
    """Verifies critical environment variables."""
    required_vars = ["NEO4J_URI", "NEO4J_PASSWORD", "GEMINI_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.error(f"❌ Missing ENV vars: {missing}")
        return False
    logger.info("✅ Environment Variables check passed.")
    return True

def check_neo4j():
    """Verifies connection to Neo4j AuraDB."""
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD") or os.getenv("NEO4J_PWD")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        with driver.session() as session:
            result = session.run("RETURN 1 as check").single()
            if result and result["check"] == 1:
                logger.info("✅ Neo4j Connection: SUCCESS")
                return True
            else:
                logger.error("❌ Neo4j Connection: Failed logic check.")
                return False
    except Exception as e:
        logger.error(f"❌ Neo4j Connection Error: {e}")
        return False

def check_gemini():
    """Verifies connection to Gemini API."""
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        # Listing models is a lightweight way to check auth
        # Note: list_models returns a generator, we just need to verify it doesn't raise AuthError
        next(genai.list_models())
        logger.info("✅ Gemini API: SUCCESS")
        return True
    except StopIteration:
        # Empty list is fine, implies Auth worked
        logger.info("✅ Gemini API: SUCCESS (No models found but Auth OK)")
        return True
    except Exception as e:
        logger.error(f"❌ Gemini API Error: {e}")
        return False

def check_volumes():
    """Verifies write permissions to Menir_Inbox volume."""
    path = "Menir_Inbox/probe_lock.tmp"
    try:
        # Require directory existence
        if not os.path.exists("Menir_Inbox"):
             logger.error("❌ Volume Error: 'Menir_Inbox' directory not found.")
             return False
             
        with open(path, "w") as f:
            f.write("probe check")
        os.remove(path)
        logger.info("✅ Volume Permissions (Menir_Inbox): SUCCESS")
        return True
    except Exception as e:
        logger.error(f"❌ Volume Permission Error: {e}")
        return False

def main():
    logger.info("🚀 Starting Pre-Flight Probe...")
    load_dotenv()
    
    checks = [
        check_env_vars(),
        check_neo4j(),
        check_gemini(),
        check_volumes()
    ]
    
    if all(checks):
        logger.info("🟢 SYSTEM READY. All checks passed.")
        sys.exit(0)
    else:
        logger.critical("🔴 SYSTEM FAILURE. Aborting launch.")
        sys.exit(1)

if __name__ == "__main__":
    main()
