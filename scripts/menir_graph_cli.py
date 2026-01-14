#!/usr/bin/env python
import argparse
import os

from neo4j import GraphDatabase
from dotenv import load_dotenv


def get_driver():
    load_dotenv()
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "menir123")
    return GraphDatabase.driver(uri, auth=(user, password))


def query_claims(session, term: str):
    cypher = """
    MATCH (c:Claim)
    WHERE toLower(c.subject) CONTAINS toLower($term)
       OR toLower(c.object)  CONTAINS toLower($term)
    RETURN
        c.id        AS id,
        c.subject   AS subject,
        c.predicate AS predicate,
        c.object    AS object,
        c.status    AS status
    ORDER BY id
    """
    return list(session.run(cypher, term=term))


def query_characters(session, term: str):
    cypher = """
    MATCH (ch:Character)
    WHERE toLower(ch.name) CONTAINS toLower($term)
    RETURN
        ch.id          AS id,
        ch.name        AS name,
        ch.visual_tags AS tags
    ORDER BY name
    """
    return list(session.run(cypher, term=term))


def main():
    parser = argparse.ArgumentParser(
        description="Menir Graph CLI (Débora / Better in Manhattan)"
    )
    parser.add_argument(
        "query",
        help="Ex: 'claims caroline' ou 'char caroline'",
    )
    args = parser.parse_args()

    raw = args.query.strip()
    parts = raw.split(maxsplit=1)
    cmd = parts[0].lower()
    term = parts[1] if len(parts) > 1 else ""

    driver = get_driver()
    try:
        with driver.session() as session:
            if cmd.startswith("claim"):
                rows = query_claims(session, term)
                print(f"Claims matching '{term}':")
                if not rows:
                    print("  (nenhum resultado)")
                    return
                for r in rows:
                    print(f"  [{r['status']}] {r['subject']} {r['predicate']} {r['object']}")
                    print(f"    ID: {r['id']}")
            elif cmd in ("char", "character", "person"):
                rows = query_characters(session, term)
                print(f"Characters matching '{term}':")
                if not rows:
                    print("  (nenhum resultado)")
                    return
                for r in rows:
                    tags = ", ".join(r["tags"] or [])
                    print(f"  {r['name']} (ID: {r['id']})")
                    if tags:
                        print(f"    Tags: {tags}")
            else:
                print("Comando não reconhecido. Use:")
                print("  claims <termo>")
                print("  char <termo>")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
