import asyncio
import glob
import logging
import os

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

from src.v3.core.menir_runner import MenirAsyncRunner  # noqa: E402
from src.v3.menir_intel import MenirIntel  # noqa: E402
from src.v3.meta_cognition import MenirOntologyManager  # noqa: E402


async def main():
    load_dotenv(override=True)
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD") or os.getenv("NEO4J_PWD")

    tenant = "BECO"
    inbox_dir = os.path.join("Menir_Inbox", tenant)
    os.makedirs(inbox_dir, exist_ok=True)

    # 1. Mock Data Generation
    dummy_file = os.path.join(inbox_dir, "fake_anomaly_test.pdf")
    with open(dummy_file, "w") as f:
        f.write("DUMMY PDF ROOT CONTENT FOR E2E TEST")

    print(f"\n[Test] Injected dummy document into Pipeline: {dummy_file}")

    manager = MenirOntologyManager(uri, (user, pwd))
    manager.bootstrap_system_graph()

    intel = MenirIntel()
    runner = MenirAsyncRunner(intel, manager)

    # We patch the analyze_payload to guarantee it hits SLOW_LANE (LLM)
    runner.invoice_skill.dispatcher.analyze_payload = lambda x: "SLOW_LANE"

    # 3. Execution
    print("\n[Test] Triggering MenirAsyncRunner._process_single_file (Watchdog simulation)...")
    await runner._process_single_file(dummy_file, tenant)

    # 4. Telemetry and Verification (Quarantine Check)
    print("\n[Test] Verifying Physical Quarantine Routing...")
    quarantine_files = glob.glob(f"Menir_Inbox/Quarantine/{tenant}/*/*")
    q_found = [f for f in quarantine_files if "fake_anomaly_test" in f]

    state_quarantine_ok = False
    if q_found:
        print(f"✅ SUCCESS: File physical routed to Quarantine -> {q_found[0]}")
        state_quarantine_ok = True
    else:
        print("❌ FAILED: File was not found in Quarantine.")

    # 5. Database Audit (Neo4j Cybernetic Check)
    print("\n[Test] Running Neo4j Forensic Graph Audit...")
    state_db_ok = False
    with manager.driver.session() as session:
        _query = """  # noqa: F841
        MATCH (i:Invoice)-[r1:RECONCILED]->(a:Anomaly)-[r2:ATTRIBUTED_TO]-(ag:Agent)   # noqa: W291
        // Note: Our cypher direction was (ag)-[:GENERATED_ANOMALY]->(a), we query in both directions to be safe
        RETURN count(a) as count
        """
        # Precise Cypher Based on our Injection
        query_precise = """
        MATCH (i:Invoice)-[r:RECONCILED]->(a:Anomaly)<-[:GENERATED_ANOMALY]-(ag:Agent)
        WHERE i.status = 'QUARANTINED'
        RETURN i.file_hash AS invoice_hash, a.type AS anomaly_type, a.count AS error_count, ag.name AS agent_name
        ORDER BY a.timestamp DESC LIMIT 1
        """

        result = session.run(query_precise)
        records = list(result)
        if records:
            print("✅ SUCCESS: Forensic Anomaly Graph successfully matched in Neo4j.")
            for r in records:
                print(f"  -> InvoiceHash: {r['invoice_hash']}")
                print(f"  -> Anomaly Type: {r['anomaly_type']}, Count: {r['error_count']}")
                print(f"  -> Attributed To: {r['agent_name']}")
            state_db_ok = True
        else:
            print("❌ FAILED: No Forensic Anomaly found in Neo4j Graph.")

    manager.close()

    if state_quarantine_ok and state_db_ok:
        print("\n🏆 E2E ANOMALY PIPELINE TEST PASSED FULLY.")
    else:
        print("\n🚨 E2E ANOMALY PIPELINE TEST FAILED.")


if __name__ == "__main__":
    asyncio.run(main())
