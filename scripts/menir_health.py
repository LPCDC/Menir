
import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "system"
SESSIONS_LOG = DATA_DIR / "menir_sessions.jsonl"

load_dotenv(override=True)

def check_db_connection() -> dict:
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        driver.close()
        return {"status": "OK", "details": f"Connected to {uri}"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def check_structure() -> dict:
    checks = {}
    
    # Check Logs
    if SESSIONS_LOG.exists():
        size = SESSIONS_LOG.stat().st_size
        checks["sessions_log"] = {"status": "OK", "details": f"Found ({size} bytes)"}
    else:
        checks["sessions_log"] = {"status": "FAIL", "error": "File not found"}
        
    return checks

def run_health_check(machine_readable=False):
    results = {
        "database": check_db_connection(),
        "structure": check_structure()
    }
    
    overall_status = "OK"
    if results["database"]["status"] != "OK":
        overall_status = "FAIL"
    for k, v in results["structure"].items():
        if v["status"] != "OK":
            overall_status = "FAIL"
            
    results["overall_status"] = overall_status

    if machine_readable:
        print(json.dumps(results, indent=2))
    else:
        print(f"🏥 Menir System Health: [{overall_status}]\n")
        
        print("1. Database Connection (AuraDB):")
        db = results["database"]
        if db["status"] == "OK":
            print(f"   ✅ {db['details']}")
        else:
            print(f"   ❌ FAILED: {db.get('error')}")
            
        print("\n2. File Structure:")
        for name, check in results["structure"].items():
            if check["status"] == "OK":
                print(f"   ✅ {name}: {check['details']}")
            else:
                print(f"   ❌ {name}: {check.get('error')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()
    
    run_health_check(args.json)
