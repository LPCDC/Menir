"""Utility script to audit the Livro Debora Neo4j graph.

The script connects to Neo4j using environment variables and prints
basic counts and sample relationship data to help validate the graph.
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Dict, Iterable, Optional

from neo4j import Driver, GraphDatabase, basic_auth
from neo4j.exceptions import Neo4jError


def get_env_variable(name: str) -> str:
    """Return the value of an environment variable or raise an error."""

    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Environment variable '{name}' is required.")
    return value


def connect_driver() -> Driver:
    """Create and return a Neo4j driver using required environment variables."""

    uri = get_env_variable("NEO4J_URI")
    user = get_env_variable("NEO4J_USER")
    password = get_env_variable("NEO4J_PASSWORD")
    return GraphDatabase.driver(uri, auth=basic_auth(user, password))


def run_query(
    driver: Driver,
    query: str,
    parameters: Optional[Dict[str, Any]] = None,
    *,
    database: Optional[str] = None,
) -> Iterable[Dict[str, Any]]:
    """Run a Cypher query and return the result records.

    Args:
        driver: Neo4j driver instance.
        query: Cypher query string.
        parameters: Optional parameters for the query.
        database: Optional database name to target.
    """

    try:
        with driver.session(database=database) as session:
            return session.run(query, parameters or {}).data()
    except Neo4jError as exc:  # pragma: no cover - runtime guard
        raise RuntimeError(f"Failed to execute query: {exc}") from exc


def print_node_counts(driver, database: Optional[str]) -> None:
    """Count nodes per label and print the results."""

    query = (
        "MATCH (n) "
        "UNWIND labels(n) AS label "
        "RETURN label, count(*) AS count "
        "ORDER BY label"
    )
    print("\n=== Node counts per label ===")
    for record in run_query(driver, query, database=database):
        print(f"{record['label']}: {record['count']}")


def print_relationship_counts(driver, database: Optional[str]) -> None:
    """Count relationships per type and print the results."""

    query = (
        "MATCH ()-[r]->() "
        "RETURN type(r) AS type, count(*) AS count "
        "ORDER BY type"
    )
    print("\n=== Relationship counts per type ===")
    for record in run_query(driver, query, database=database):
        print(f"{record['type']}: {record['count']}")


def print_character_relationships(driver, database: Optional[str]) -> None:
    """List relationships between Character nodes, if any."""

    query = (
        "MATCH (c1:Character)-[r]->(c2:Character) "
        "RETURN c1.name AS from_name, type(r) AS rel, c2.name AS to_name "
        "ORDER BY rel, from_name, to_name"
    )
    print("\n=== Character to Character relationships ===")
    results = list(run_query(driver, query, database=database))
    if not results:
        print("No direct Character-to-Character relationships found.")
        return

    for record in results:
        from_name = record.get("from_name", "<unnamed>")
        to_name = record.get("to_name", "<unnamed>")
        print(f"{from_name} —{record['rel']}→ {to_name}")


def print_relationship_samples(driver, database: Optional[str], limit: int) -> None:
    """Print a sample of arbitrary relationships for manual inspection."""

    query = (
        "MATCH (a)-[r]->(b) "
        "RETURN coalesce(head(labels(a)), 'Node') AS from_label, id(a) AS from_id, "
        "type(r) AS rel, coalesce(head(labels(b)), 'Node') AS to_label, id(b) AS to_id "
        "LIMIT $limit"
    )
    print(f"\n=== Sample relationships (up to {limit}) ===")
    results = run_query(driver, query, {"limit": limit}, database=database)
    any_result = False
    for record in results:
        any_result = True
        print(
            f"{record['from_label']}({record['from_id']}) "
            f"—{record['rel']}→ "
            f"{record['to_label']}({record['to_id']})"
        )
    if not any_result:
        print("No relationships found to sample.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the Livro Debora Neo4j graph")
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=200,
        help="Maximum number of sample relationships to print (default: 200)",
    )
    parser.add_argument(
        "--skip-sample",
        action="store_true",
        help="Skip printing sample relationships",
    )
    args = parser.parse_args()

    database = os.getenv("NEO4J_DB")
    driver: Optional[Driver] = None

    try:
        driver = connect_driver()
        driver.verify_connectivity()
        print("Connected to Neo4j successfully.")

        print_node_counts(driver, database)
        print_relationship_counts(driver, database)
        print_character_relationships(driver, database)
        if not args.skip_sample:
            print_relationship_samples(driver, database, args.sample_limit)
    except (EnvironmentError, RuntimeError, Neo4jError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        if driver:
            try:
                driver.close()
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
