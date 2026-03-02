#!/usr/bin/env python3
# scripts/migrate_normalize_chapter1.py
# Normalizes functionality for Chapter 1 graph data (Slugs, Merges, Provenance)

import os
import sys
import re
import unicodedata
from neo4j import GraphDatabase, basic_auth

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Secure credential loading
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PWD = os.getenv("NEO4J_PWD") or os.getenv("NEO4J_PASSWORD")

if not all([NEO4J_URI, NEO4J_USER, NEO4J_PWD]):
    print("ERRO: Credenciais Neo4j ausentes no .env")
    sys.exit(1)

def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PWD))

def slugify(text):
    if not text: return ""
    # Normalize unicode, lower, remove non-alphanumeric (keep underscores), collapse spaces
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text

def main():
    driver = get_driver()
    
    # Verify connectivity
    try:
        driver.verify_connectivity()
        print("[INFO] Connected to Neo4j.")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        sys.exit(1)

    with driver.session() as session:
        print("=== Step 1: Creating Constraints ===")
        constraints = [
            "CREATE CONSTRAINT character_entity_id_unique IF NOT EXISTS FOR (c:Character) REQUIRE c.entity_id IS UNIQUE",
            "CREATE CONSTRAINT place_entity_id_unique IF NOT EXISTS FOR (p:Place) REQUIRE p.entity_id IS UNIQUE",
            "CREATE CONSTRAINT scene_entity_id_unique IF NOT EXISTS FOR (s:Scene) REQUIRE s.entity_id IS UNIQUE",
            "CREATE CONSTRAINT event_entity_id_unique IF NOT EXISTS FOR (e:Event) REQUIRE e.entity_id IS UNIQUE"
        ]
        for c in constraints:
            session.run(c)
            print(f"Applied: {c}")

        print("\n=== Step 2: Normalizing Nodes (Slugify + Merge) ===")
        # Support for Character and Place initially
        labels = ["Character", "Place"]
        
        for label in labels:
            print(f"\nProcessing Label: {label}")
            # Get all nodes without entity_id or just all nodes to ensure consistency
            # Strategy: Fetch all, calculate slug, merge.
            fetch_query = f"MATCH (n:{label}) RETURN elementId(n) as id, n.name as name, n.canonical_name as cname"
            nodes = session.run(fetch_query).data()
            
            merged_count = 0
            
            for record in nodes:
                node_id = record['id']
                name = record['name'] or record['cname']
                
                if not name:
                    print(f"[WARN] Node {node_id} has no name property. Skipping.")
                    continue
                    
                slug = slugify(name)
                
                # We use a transaction for the merge to ensure safety
                # Using APOC for refactoring if available
                merge_query = f"""
                MATCH (target) WHERE elementId(target) = $node_id
                MERGE (canon:{label} {{entity_id: $slug}})
                ON CREATE SET canon.name = $name
                WITH target, canon
                WHERE target <> canon
                CALL apoc.refactor.mergeNodes([canon, target], {{properties: "combine", mergeRels: true}})
                YIELD node
                RETURN count(node) as merged
                """
                
                try:
                    result = session.run(merge_query, node_id=node_id, slug=slug, name=name)
                    summary = result.single()
                    if summary and summary['merged'] > 0:
                        merged_count += 1
                        # print(f"Merged {name} -> {slug}")
                except Exception as e:
                    print(f"[ERROR] Failed to merge {name} ({slug}): {e}")
                    # Likely APOC missing or constraint violation if logic is flawed
                    if "apoc" in str(e).lower():
                        print("CRITICAL: APOC plugin appears to be missing. Cannot execute merge.")
                        sys.exit(1)

            print(f"[{label}] Processed {len(nodes)} nodes. Merged/Normalized operations: {merged_count}")

            # Fallback/Consistency: Ensure the original node HAS the entity_id if it was the canon one
            # (The merge logic merges INTO canon, so canon survives. If target was already canon, nothing happened effectively besides maybe property update)
            
        print("\n=== Step 3: Provenance Metadata ===")
        # Add metadata to nodes missing source_file
        prov_query = """
        MATCH (n)
        WHERE (n:Character OR n:Place OR n:Scene OR n:Event) AND n.source_file IS NULL
        SET n.source_file = "legacy_chapter1_import",
            n.proposal_id = "initial_migration",
            n.source_timestamp = datetime()
        RETURN count(n) as updated
        """
        res = session.run(prov_query).single()
        print(f"Updated provenance for {res['updated']} legacy nodes.")

        print("\n=== Step 4: Final Audit ===")
        audit_query = """
        MATCH (c1:Character), (c2:Character)
        WHERE c1 <> c2 AND c1.entity_id = c2.entity_id
        RETURN c1.name, c2.name
        """
        audit_res = session.run(audit_query).data()
        if len(audit_res) == 0:
            print("[SUCCESS] No duplicate Character entity_ids found.")
        else:
            print(f"[WARN] Found {len(audit_res)} duplicates:")
            for row in audit_res:
                print(row)

    driver.close()

if __name__ == "__main__":
    main()
