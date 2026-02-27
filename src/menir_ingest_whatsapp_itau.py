#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingestão: Mensagens WhatsApp JSONL → Neo4j (Document + Message/Event)

Usage:
  python3 scripts/menir_ingest_whatsapp_itau.py \
    --input data/itau/whatsapp/normalized/whatsapp_messages.jsonl \
    --uri bolt://localhost:7687 \
    --user neo4j \
    --password menir123 \
    --db neo4j \
    --project PROJECT_ITAU_15220012
"""

import json
import argparse
import os
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError


def parse_args():
    p = argparse.ArgumentParser(description="Ingestão WhatsApp Itaú → Neo4j")
    p.add_argument("--input", required=True, help="Arquivo JSONL de mensagens")
    p.add_argument("--uri", required=True, help="Neo4j URI")
    p.add_argument("--user", required=True, help="Neo4j username")
    p.add_argument("--password", required=True, help="Neo4j password")
    p.add_argument("--db", required=True, help="Database name")
    p.add_argument("--project", required=True, help="Project ID")
    return p.parse_args()


def main():
    args = parse_args()

    if not os.path.exists(args.input):
        print(f"✗ Input file not found: {args.input}")
        return False

    try:
        driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
        driver.verify_connectivity()
        print(f"✓ Connected to {args.uri}")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

    total = 0
    errors = 0

    try:
        with driver.session(database=args.db) as sess:
            with open(args.input, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        m = json.loads(line)

                        # Sanitize message ID
                        msg_id = m.get("message_id", f"wh_msg_{line_num}")
                        if not msg_id:
                            msg_id = f"wh_msg_{line_num}"

                        # Execute ingestion
                        sess.run(
                            """
                            MERGE (p:Project {id: $project})
                            CREATE (d:Document {
                                id: $msg_id,
                                source: 'whatsapp',
                                date: $date,
                                chat_id: $chat_id,
                                author: $author,
                                text: $text,
                                tags: $tags
                            })
                            CREATE (p)-[:HAS_DOC]->(d)
                            """,
                            project=args.project,
                            msg_id=msg_id,
                            date=m.get("datetime"),
                            chat_id=m.get("chat_id"),
                            author=m.get("author"),
                            text=m.get("text"),
                            tags=m.get("tags", [])
                        )

                        total += 1

                    except json.JSONDecodeError:
                        errors += 1
                        print(f"  ⚠ Line {line_num}: Invalid JSON")
                    except Neo4jError as e:
                        errors += 1
                        print(f"  ⚠ Line {line_num}: Neo4j error: {e}")
                    except Exception as e:
                        errors += 1
                        print(f"  ⚠ Line {line_num}: {e}")

    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        driver.close()

    print(f"\n✅ Ingested {total} messages ({errors} errors)")
    return errors == 0


if __name__ == "__main__":
    ok = main()
    exit(0 if ok else 1)
