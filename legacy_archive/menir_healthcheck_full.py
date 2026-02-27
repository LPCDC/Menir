#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menir full health check with project document counting.

Validates:
- Neo4j connectivity and basic operations
- Global node/relation counts
- Per-project document counts (assumes Project-[HAS_DOC]->Document structure)

Environment:
  NEO4J_URI         - Connection URI (default: bolt://localhost:7687)
  NEO4J_USER        - Username (default: neo4j)
  NEO4J_PWD         - Password (required; no default)
  NEO4J_DB          - Database name (default: neo4j)
  MENIR_HEALTH_OUTPUT - Output JSON path (default: menir_health_status.json)

Output:
  menir_health_status.json - JSON report with connectivity, node/rel counts, per-project docs

Exit code:
  0 - healthy (connected, queries successful)
  1 - error (unreachable, query failed)
"""

import os
import json
import sys
from datetime import datetime, timezone

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable, AuthError


# --- Configuration via environment ---
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PWD = os.getenv("NEO4J_PWD", None)
DB = os.getenv("NEO4J_DB", "neo4j")

OUTPUT_PATH = os.getenv("MENIR_HEALTH_OUTPUT", "menir_health_status.json")

# List of expected project IDs (customize as needed)
PROJECT_IDS = [
    "PROJECT_ITAU_15220012",
    "PROJECT_TIVOLI",
    "PROJECT_IBERE",
    "PROJECT_LIVRO_DEBORA",
    "PROJECT_SAINT_CHARLES",
    "PROJECT_MENIR_OS"
]


def make_driver():
    """Create Neo4j driver instance."""
    return GraphDatabase.driver(URI, auth=(USER, PWD))


def smoke_test(session):
    """Run trivial query to verify session works."""
    session.run("RETURN 1").single()


def count_nodes_rels(session):
    """Count total nodes and relationships in database."""
    node_count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
    rel_count = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
    return node_count, rel_count


def count_project_docs(session, pid):
    """Count documents for a specific project."""
    q = """
    MATCH (p:Project {id: $pid})-[:HAS_DOC]->(d:Document)
    RETURN count(d) AS docs
    """
    res = session.run(q, pid=pid)
    r = res.single()
    return r["docs"] if r else 0


def run_health_check():
    """Execute full health check: connectivity, queries, project counts."""
    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "neo4j": {
            "uri": URI,
            "status": None,
            "node_count": None,
            "rel_count": None,
            "error": None
        },
        "projects": {},
        "warnings": []
    }

    # Try connection
    try:
        driver = make_driver()
        driver.verify_connectivity()
    except (ServiceUnavailable, AuthError, Neo4jError) as e:
        report["neo4j"]["status"] = "unreachable"
        report["neo4j"]["error"] = str(e)
        return report

    # Run queries
    with driver.session(database=DB) as session:
        try:
            smoke_test(session)
            n, r = count_nodes_rels(session)
            report["neo4j"]["status"] = "ok"
            report["neo4j"]["node_count"] = n
            report["neo4j"]["rel_count"] = r

            # Count documents per project
            for pid in PROJECT_IDS:
                docs = count_project_docs(session, pid)
                report["projects"][pid] = {"doc_count": docs}

        except Neo4jError as e:
            report["neo4j"]["status"] = "error"
            report["neo4j"]["error"] = str(e)

    driver.close()
    return report


def save_report(report, path):
    """Save report to JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def main():
    """Execute health check and output results."""
    rpt = run_health_check()
    save_report(rpt, OUTPUT_PATH)

    status = rpt["neo4j"]["status"]
    print(f"Health-check result: {status}")

    if status == "ok":
        print(f"Nodes: {rpt['neo4j']['node_count']}, Rels: {rpt['neo4j']['rel_count']}")
        print("Per-project doc counts:")
        for pid, info in rpt["projects"].items():
            doc_count = info['doc_count']
            print(f"  {pid}: {doc_count} docs")
        sys.exit(0)
    else:
        print("Error / unreachable:", rpt["neo4j"].get("error"))
        sys.exit(1)


if __name__ == "__main__":
    main()
