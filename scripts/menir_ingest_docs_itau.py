#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingestão: Documentos gerais (contratos, declarações, prints) manifest → Neo4j

Usage:
  python3 scripts/menir_ingest_docs_itau.py \
    --input data/itau/docs/itau_docs_manifest.json \
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
    p = argparse.ArgumentParser(description="Ingestão docs Itaú → Neo4j")
    p.add_argument("--input", required=True, help="Arquivo JSON manifest de documentos")
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
        with open(args.input, encoding="utf-8") as f:
            docs = json.load(f)

        if not isinstance(docs, list):
            print(f"✗ Invalid manifest format: expected list of documents")
            return False

        with driver.session(database=args.db) as sess:
            for idx, doc in enumerate(docs, 1):
                try:
                    # Use hash as document ID (must be unique)
                    doc_id = doc.get("hash_sha256")
                    if not doc_id:
                        doc_id = f"doc_{idx}"

                    # Execute ingestion
                    sess.run(
                        """
                        MERGE (p:Project {id: $project})
                        CREATE (d:Document {
                            id: $doc_id,
                            source: 'file',
                            path: $path,
                            filename: $filename,
                            doc_type: $doc_type,
                            size_bytes: $size_bytes
                        })
                        CREATE (p)-[:HAS_DOC]->(d)
                        """,
                        project=args.project,
                        doc_id=doc_id,
                        path=doc.get("path"),
                        filename=doc.get("filename"),
                        doc_type=doc.get("type", "UNKNOWN"),
                        size_bytes=doc.get("size_bytes", 0)
                    )

                    total += 1

                except Neo4jError as e:
                    errors += 1
                    print(f"  ⚠ Doc {idx}: Neo4j error: {e}")
                except Exception as e:
                    errors += 1
                    print(f"  ⚠ Doc {idx}: {e}")

    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        driver.close()

    print(f"\n✅ Ingested {total} documents ({errors} errors)")
    return errors == 0


if __name__ == "__main__":
    ok = main()
    exit(0 if ok else 1)
