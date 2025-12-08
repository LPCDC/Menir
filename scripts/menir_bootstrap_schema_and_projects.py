#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menir bootstrap: minimal schema + anchor projects.

Creates:
1. Base schema: Project label + constraints
2. Anchor projects: ITAU, TIVOLI, IBERE, LIVRO_DEBORA, SAINT_CHARLES, MENIR_OS

Environment:
  NEO4J_URI      - Bolt URI (default: bolt://localhost:7687)
  NEO4J_USER     - Username (default: neo4j)
  NEO4J_PWD      - Password (default: menir123)
  NEO4J_DB       - Database (default: neo4j)

Exit code:
  0 - schema and projects created
  1 - error during creation
"""

import os
import sys
from datetime import datetime, timezone

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError


URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PWD = os.getenv("NEO4J_PWD", "menir123")
DB = os.getenv("NEO4J_DB", "neo4j")

# Anchor projects
ANCHOR_PROJECTS = [
    {"id": "PROJECT_ITAU_15220012", "name": "Itau Banking"},
    {"id": "PROJECT_TIVOLI", "name": "Tivoli OS"},
    {"id": "PROJECT_IBERE", "name": "Ibere Analytics"},
    {"id": "PROJECT_LIVRO_DEBORA", "name": "Livro Débora"},
    {"id": "PROJECT_SAINT_CHARLES", "name": "Saint Charles"},
    {"id": "PROJECT_MENIR_OS", "name": "Menir OS"},
]


def bootstrap_schema(session):
    """Create base schema with Project label and constraints."""
    print("[1] Creating schema...")

    # Create Project constraint
    session.run(
        "CREATE CONSTRAINT project_id_unique IF NOT EXISTS "
        "FOR (p:Project) REQUIRE p.id IS UNIQUE"
    )
    print("    ✓ Project ID constraint")

    # Create index on Project id
    session.run(
        "CREATE INDEX project_id_idx IF NOT EXISTS "
        "FOR (p:Project) ON (p.id)"
    )
    print("    ✓ Project ID index")

    # Create index on Project created_at
    session.run(
        "CREATE INDEX project_created_at_idx IF NOT EXISTS "
        "FOR (p:Project) ON (p.created_at)"
    )
    print("    ✓ Project created_at index")


def create_anchor_projects(session):
    """Create anchor project nodes."""
    print("[2] Creating anchor projects...")

    now = datetime.now(timezone.utc).isoformat()

    for proj in ANCHOR_PROJECTS:
        session.run(
            """
            MERGE (p:Project {id: $id})
            ON CREATE SET
              p.name = $name,
              p.created_at = $created_at,
              p.status = 'active'
            RETURN p.id AS project_id
            """,
            id=proj["id"],
            name=proj["name"],
            created_at=now,
        )
        print(f"    ✓ {proj['id']}")


def verify_setup(session):
    """Verify schema and projects were created."""
    print("[3] Verifying setup...")

    # Count projects
    res = session.run("MATCH (p:Project) RETURN count(p) AS c").single()
    count = res["c"]
    print(f"    ✓ Projects created: {count}")

    # List projects
    res = session.run("MATCH (p:Project) RETURN p.id AS id, p.name AS name ORDER BY p.id")
    for record in res:
        print(f"      - {record['id']}: {record['name']}")

    return count == len(ANCHOR_PROJECTS)


def main():
    """Execute bootstrap."""
    try:
        driver = GraphDatabase.driver(URI, auth=(USER, PWD))
        driver.verify_connectivity()
        print(f"✓ Connected to {URI}")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

    try:
        with driver.session(database=DB) as session:
            bootstrap_schema(session)
            create_anchor_projects(session)
            verified = verify_setup(session)

            if verified:
                print("\n✅ Bootstrap complete: schema + 6 anchor projects")
                return True
            else:
                print("\n✗ Bootstrap incomplete: verification failed")
                return False

    except Neo4jError as e:
        print(f"\n✗ Error during bootstrap: {e}")
        return False
    finally:
        driver.close()


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
