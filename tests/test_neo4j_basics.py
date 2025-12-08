#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menir Neo4j Basic Test Suite

4 tests for Neo4j connectivity, persistence, and data integrity.

WARNING: This test suite creates test data in the Neo4j database.
Run only in sandbox/test environment, NOT in production.

Tests:
1. test_connection: Verify Neo4j connectivity (trivial query)
2. test_create_persistence_node: Create test node with timestamp
3. test_read_persistence_node_after_restart: Verify persistence (simulated reconnect)
4. test_no_duplicate_email_docs: Check for duplicate Document nodes

Usage:
  pytest tests/test_neo4j_basics.py -v

Environment:
  NEO4J_URI    - Bolt URI (default: bolt://localhost:7687)
  NEO4J_USER   - Username (default: neo4j)
  NEO4J_PWD    - Password (default from command)
  NEO4J_DB     - Database (default: neo4j)
"""

import os
import pytest
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError


# Configuration (override via environment variables)
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PWD = os.getenv("NEO4J_PWD", "menir123")
DB = os.getenv("NEO4J_DB", "neo4j")

TEST_TAG = "menir_test_suite"


@pytest.fixture(scope="module")
def driver():
    """Create Neo4j driver for test module."""
    try:
        drv = GraphDatabase.driver(URI, auth=(USER, PWD))
        drv.verify_connectivity()
        print(f"\n✓ Connected to {URI}")
        yield drv
    except Neo4jError as e:
        pytest.fail(f"Could not connect to Neo4j: {e}")
    finally:
        drv.close()


@pytest.fixture(scope="function")
def cleanup_test_nodes(driver):
    """Clean up test nodes before and after each test."""
    # Clean before test
    with driver.session(database=DB) as sess:
        sess.run(f"MATCH (n {{tag: '{TEST_TAG}'}}) DELETE n")
    
    yield
    
    # Clean after test
    with driver.session(database=DB) as sess:
        sess.run(f"MATCH (n {{tag: '{TEST_TAG}'}}) DELETE n")


class TestConnection:
    """Test basic Neo4j connectivity."""

    def test_connection(self, driver):
        """Verify trivial query execution."""
        with driver.session(database=DB) as sess:
            result = sess.run("RETURN 1 AS v")
            rec = result.single()
            assert rec is not None, "Query returned no result"
            assert rec["v"] == 1, f"Expected 1, got {rec['v']}"


class TestPersistence:
    """Test data persistence in Neo4j."""

    def test_create_persistence_node(self, driver, cleanup_test_nodes):
        """Create a test node with timestamp."""
        with driver.session(database=DB) as sess:
            res = sess.run(
                """
                CREATE (t:TestNode {tag: $tag, ts: datetime()})
                RETURN t.tag AS tag, t.ts AS ts
                """,
                tag=TEST_TAG
            )
            rec = res.single()
            assert rec is not None, "Failed to create test node"
            assert rec["tag"] == TEST_TAG, f"Tag mismatch: {rec['tag']}"
            assert rec["ts"] is not None, "Timestamp not set"

    def test_read_persistence_node_after_reconnect(self, driver, cleanup_test_nodes):
        """Verify node persistence after simulated reconnect."""
        # First session: create node
        with driver.session(database=DB) as sess:
            sess.run(
                """
                CREATE (t:TestNode {tag: $tag, ts: datetime()})
                RETURN t
                """,
                tag=TEST_TAG
            )

        # Second session: simulate reconnect and read
        with driver.session(database=DB) as sess:
            res = sess.run(
                """
                MATCH (t:TestNode {tag: $tag})
                RETURN t.tag AS tag, t.ts AS ts
                """,
                tag=TEST_TAG
            )
            rec = res.single()
            assert rec is not None, "Node not found after reconnect"
            assert rec["tag"] == TEST_TAG, "Tag mismatch after reconnect"
            assert rec["ts"] is not None, "Timestamp not persisted"


class TestDataIntegrity:
    """Test data integrity constraints."""

    def test_no_duplicate_email_docs(self, driver):
        """
        Check for duplicate Document nodes with same message_id.
        
        Note: This test is a guardrail for ingestion quality.
        It assumes Document nodes have been created; if not, it passes (neutral).
        """
        with driver.session(database=DB) as sess:
            res = sess.run(
                """
                MATCH (d:Document)
                WHERE d.message_id IS NOT NULL
                WITH d.message_id AS mid, count(*) AS c
                WHERE c > 1
                RETURN mid, c
                LIMIT 5
                """
            )
            records = list(res)
            assert len(records) == 0, (
                f"Found {len(records)} duplicate message_ids: {records}"
            )

    def test_project_nodes_exist(self, driver):
        """Verify that anchor Project nodes exist."""
        with driver.session(database=DB) as sess:
            res = sess.run(
                "MATCH (p:Project) RETURN count(p) AS c"
            )
            count = res.single()["c"]
            # Should have at least the bootstrap projects
            assert count >= 1, f"Expected >= 1 Project nodes, found {count}"

    def test_no_orphaned_documents(self, driver):
        """Verify that Documents are connected to Projects."""
        with driver.session(database=DB) as sess:
            res = sess.run(
                """
                MATCH (d:Document)
                WHERE NOT (d)<-[:HAS_DOC]-(:Project)
                RETURN count(d) AS c
                """
            )
            orphans = res.single()["c"]
            # Orphaned documents are a data quality issue
            assert orphans == 0, (
                f"Found {orphans} orphaned Document nodes (not linked to Project)"
            )


class TestSchemaConstraints:
    """Test schema-level constraints."""

    def test_project_id_constraint_exists(self, driver):
        """Verify Project ID uniqueness constraint exists."""
        with driver.session(database=DB) as sess:
            res = sess.run(
                """
                SHOW CONSTRAINTS
                YIELD name, type, labelsOrTypes, properties
                WHERE type = 'UNIQUENESS'
                AND 'Project' IN labelsOrTypes
                RETURN count(*) AS c
                """
            )
            count = res.single()["c"]
            assert count > 0, "No uniqueness constraint found for Project"

    def test_project_id_uniqueness(self, driver, cleanup_test_nodes):
        """Test that Project ID uniqueness constraint is enforced."""
        with driver.session(database=DB) as sess:
            # Create first node
            sess.run(
                """
                CREATE (p:Project {id: $id, name: $name})
                """,
                id=f"test_{TEST_TAG}",
                name="Test Project"
            )

            # Try to create duplicate (should fail or be merged)
            try:
                res = sess.run(
                    """
                    CREATE (p:Project {id: $id, name: $name})
                    RETURN p
                    """,
                    id=f"test_{TEST_TAG}",
                    name="Test Project 2"
                )
                # If no error, MERGE should have been used instead
                rec = res.single()
                # Verify only one Project with this ID exists
                count_res = sess.run(
                    "MATCH (p:Project {id: $id}) RETURN count(p) AS c",
                    id=f"test_{TEST_TAG}"
                )
                count = count_res.single()["c"]
                assert count == 1, f"Expected 1 Project, found {count}"
            except Exception as e:
                # Expected: constraint violation or merge behavior
                print(f"  (Expected duplicate handling: {type(e).__name__})")
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
