#!/usr/bin/env python3
import os
import sys
import json
import jsonlines
import logging
from pathlib import Path
from datetime import datetime
from neo4j import GraphDatabase

# Setup Paths
BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(BASE_DIR))

try:
    from menir_core.ingest.extractor import MenirExtractor
except ImportError:
    MenirExtractor = None

# Config
DATA_DIR = BASE_DIR / "data"
PROPOSALS_DIR = DATA_DIR / "proposals" / "inbox"
ARCHIVE_DIR = DATA_DIR / "proposals" / "archive"

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "menir123")

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("menir_applicator")

def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Initialize Extractor
extractor = MenirExtractor() if MenirExtractor else None

def proposal_already_applied(tx, proposal_id):
    """Check if proposal ID exists in ProposalLog."""
    result = tx.run("MATCH (l:ProposalLog {id: $pid}) RETURN l", pid=proposal_id)
    return result.single() is not None

def apply_node_op(tx, node_op):
    """Execute dynamic Node MERGE/SET."""
    # naive implementation for V1 generic nodes
    # Expects: {"id": "uid", "labels": ["Label"], "properties": {...}}
    labels = ":".join(node_op.get("labels", []))
    props = node_op.get("properties", {})
    uid = node_op.get("id")
    
    if not labels or not uid:
        logger.warning(f"Skipping invalid node op: {node_op}")
        return

    # Dynamic Cypher construction (Be careful with injection if public, but this is internal tool)
    # We use params for values, but label string must be sanitized or trusted.
    # Assuming trusted proposals for now.
    query = f"MERGE (n:`{labels}` {{id: $uid}}) SET n += $props" # Corrected string interpolation
    # Fix: labels list might not work as label param directly in Cypher without APOC.
    # We construct the Label string. If multiple labels, this needs loop logic or APOC.
    # Simplified: Assume primary label for now or use APOC labels.
    # Let's handle list of labels:
    label_str = ":".join([f"`{l}`" for l in node_op.get("labels", [])])
    
    cypher = f"MERGE (n:{label_str} {{id: $uid}}) SET n += $props"
    tx.run(cypher, uid=uid, props=props)

def apply_rel_op(tx, rel_op):
    """Execute dynamic Relationship MERGE."""
    # Expects: {"source": "uid1", "target": "uid2", "type": "REL_TYPE", "properties": {}}
    src = rel_op.get("source")
    tgt = rel_op.get("target")
    rtype = rel_op.get("type")
    props = rel_op.get("properties", {})
    
    cypher = f"""
    MATCH (a {{id: $src}}), (b {{id: $tgt}})
    MERGE (a)-[r:`{rtype}`]->(b)
    SET r += $props
    """
    tx.run(cypher, src=src, tgt=tgt, props=props)

def apply_proposal_tx(tx, data):
    proposal_id = data.get("proposal_id") or data.get("op_id")
    if not proposal_id:
        # Fallback: if no ID, generate one or skip?
        # For raw cypher ops, we might accept missing ID if allowed.
        # But logging needs ID.
        logger.warning(f"Proposal/Op missing ID in data: {data.keys()}")
        raise ValueError("Proposal missing ID")
        
    if proposal_already_applied(tx, proposal_id):
        logger.warning(f"Skipping {proposal_id} (Already Applied)")
        return False

    logger.info(f"Applying Proposal {proposal_id}...")
    
    # Handler for 'create_node' (Pilot 3)
    if data.get("type") == "create_node":
        payload = data.get("payload", {})
        label = payload.get("label", "Generic")
        props = payload.get("properties", {})
        
        # Sanitize label (simple alphanumeric check or backtick escape)
        # Using backticks is safer for Cypher
        cypher = f"MERGE (n:`{label}` {{name: $props.name}}) SET n += $props RETURN n"
        tx.run(cypher, props=props)
        logger.info(f"Created node :{label} with props {props}")

    # Handler for 'create_rel' (Phase 10)
    if data.get("type") == "create_rel":
        payload = data.get("payload", {})
        start = payload.get("start", {})
        end = payload.get("end", {})
        rel = payload.get("rel", "RELATED_TO").upper().replace(" ", "_")
        props = payload.get("properties", {})
        
        # Validation
        if not (start and end and rel):
            logger.warning(f"Invalid create_rel payload: {payload}")
            return
            
        s_label = start.get("label", "Generic")
        s_name = start.get("name")
        e_label = end.get("label", "Generic")
        e_name = end.get("name")
        
        if not (s_name and e_name):
             logger.warning(f"Missing names for relationship sync: {start} -> {end}")
             return

        # Cypher (Dynamic Label Injection - Internal Trusted)
        cypher = f"""
        MATCH (a:`{s_label}` {{name: $s_name}}), (b:`{e_label}` {{name: $e_name}})
        MERGE (a)-[r:`{rel}`]->(b)
        SET r += $props
        """
        tx.run(cypher, s_name=s_name, e_name=e_name, props=props)
        logger.info(f"Linked ({s_name})-[{rel}]->({e_name})")

    # Handler for 'ingest_file' (Pilot 4)
    if data.get("type") == "ingest_file":
        payload = data.get("payload", {})
        filepath = payload.get("filepath")
        
        if filepath:
            filename = os.path.basename(filepath)
            props = {
                "filename": filename,
                "original_path": filepath,
                "status": "ingested",
                "ingested_at": datetime.now().isoformat()
            }
            cypher = "CREATE (d:Document) SET d += $props RETURN d"
            tx.run(cypher, props=props)
            logger.info(f"Created Document node for {filename}")

            # Hybrid Brain Extraction (Pilot 5)
            if extractor and os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        text_content = f.read()
                    
                    logger.info(f"Extracted text ({len(text_content)} chars). analyzing with Gemini...")
                    knowledge = extractor.extract_knowledge(text_content)
                    
                    if "error" in knowledge:
                        logger.error(f"Gemini Error: {knowledge['error']}")
                    else:
                        # Create Entities
                        for entity in knowledge.get("entities", []):
                            e_props = {"name": entity.get("name"), "description": entity.get("description")}
                            label = entity.get("label", "Concept").replace(" ", "")
                            # Sanitization
                            if not label.isalnum(): label = "Concept"
                            
                            q = f"MERGE (e:`{label}` {{name: $name}}) SET e += $props"
                            tx.run(q, name=e_props["name"], props=e_props)

                        # Create Relationships
                        for rel in knowledge.get("relationships", []):
                            r_type = rel.get("type", "RELATED_TO").upper().replace(" ", "_")
                            q = f"""
                            MATCH (a {{name: $src}}), (b {{name: $tgt}})
                            MERGE (a)-[r:`{r_type}`]->(b)
                            SET r.description = $desc
                            """
                            tx.run(q, src=rel["source"], tgt=rel["target"], desc=rel.get("description"))

                        # Link Entities to Document
                        for entity in knowledge.get("entities", []):
                            q = "MATCH (d:Document {original_path: $path}), (e {name: $name}) MERGE (d)-[:MENTIONS]->(e)"
                            tx.run(q, path=filepath, name=entity["name"])

                        logger.info(f"Graph Enriched with {len(knowledge.get('entities', []))} entities.")

                        # Context Enrichment (Tavily)
                        if knowledge.get("search_intents"):
                            logger.info(f"Processing Search Intents: {knowledge['search_intents']}")
                            for query in knowledge["search_intents"]:
                                search_res = extractor.enrich_context(query)
                                if search_res and "results" in search_res:
                                    for res in search_res["results"][:2]: # Top 2
                                        f_props = {"content": res["content"], "url": res["url"], "query": query}
                                        q = """
                                        MATCH (d:Document {original_path: $path})
                                        CREATE (f:ExternalFact) SET f += $props
                                        CREATE (d)-[:HAS_CONTEXT]->(f)
                                        """
                                        tx.run(q, path=filepath, props=f_props)
                                    logger.info(f"Added context from Tavily for '{query}'")

                except Exception as e:
                    logger.error(f"Extraction Logic Failed: {e}")
            else:
                logger.warning("Extractor not available or file not found.")

        else:
            logger.warning("ingest_file proposal missing filepath")

    # Handler for 'raw_cypher' (v4.1.2 Admin Delta)
    if data.get("cypher"):
         query = data.get("cypher")
         desc = data.get("description", "Raw Cypher Op")
         logger.info(f"Executing Raw Cypher: {desc}")
         tx.run(query)
         # Return to avoid following legacy blocks if mixed? No, just continue.


    # Legacy V1 Logic (Optional, keeping for compatibility if mixed)
    if data.get("nodes"):
        for node in data.get("nodes", []):
            apply_node_op(tx, node)
            
    if data.get("relationships"):
        for rel in data.get("relationships", []):
            apply_rel_op(tx, rel)
        
    # Create Log
    tx.run("""
        CREATE (:ProposalLog {
            id: $pid, 
            applied_at: datetime(), 
            project_id: $proj,
            type: $type
        })
    """, pid=proposal_id, proj=data.get("project_id"), type=data.get("type"))
    
    return True

def process_file(filepath: Path, driver, commit: bool):
    """Read file, process content, manage state."""
    logger.info(f"Reading {filepath.name}...")
    
    try:
        if filepath.suffix == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                proposals = json.load(f)
        else:
             with jsonlines.open(filepath) as reader:
                proposals = list(reader)
    except Exception as e:
        logger.error(f"Failed to parse {filepath}: {e}")
        return

    # Support for standard JSON envelope (v4.1.2 Delta Format)
    if isinstance(proposals, dict) and "operations" in proposals:
        logger.info(f"Detected Delta Envelope: {proposals.get('meta', {}).get('proposal_id')}")
        proposals = proposals["operations"]
    elif isinstance(proposals, dict):
         proposals = [proposals]
    # Else it is a list from jsonlines

    for data in proposals:
        if data.get("status") == "applied":
            logger.info(f"Skipping {data.get('proposal_id')} (Status applied inside file)")
            continue

        if commit:
            with driver.session() as session:
                try:
                    result = session.execute_write(apply_proposal_tx, data)
                    if result:
                        logger.info(f"✅ Proposal {data.get('proposal_id')} applied.")
                except Exception as e:
                    logger.error(f"❌ Transaction failed for {data.get('proposal_id')}: {e}")
        else:
            logger.info(f"Dry Run: Would apply {data.get('proposal_id')}")

    # Move to archive after processing all (or partial?)
    # For now, archive if at least one processed or file consumed? 
    # Logic: If we iterate, we assume success. 
    # In rigorous system, we'd rewrite file Removing applied lines.
    # Simple Logic: Move entire file to archive.
    if commit:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        new_path = ARCHIVE_DIR / filepath.name
        # If exists, overwrite or append timestamp?
        if new_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_path = ARCHIVE_DIR / f"{filepath.stem}_{timestamp}.jsonl"
            
        # filepath.rename(new_path) # rename fails on cross-device
        import shutil
        shutil.move(str(filepath), str(new_path))
        logger.info(f"Archived file to {new_path}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Menir Proposal Applicator")
    parser.add_argument("--commit", action="store_true", help="Commit changes to DB")
    parser.add_argument("--file", help="Specific file to apply")
    args = parser.parse_args()

    # Check Proposals Dir
    if not PROPOSALS_DIR.exists():
        logger.info("No proposals directory found.")
        return

    files = [Path(args.file)] if args.file else list(PROPOSALS_DIR.glob("*.jsonl"))
    
    if not files:
        logger.info("No pending proposals found.")
        return

    driver = get_driver()
    try:
        driver.verify_connectivity()
    except Exception as e:
        logger.error(f"Cannot connect to Neo4j: {e}")
        return

    for f in files:
        if f.is_file():
            process_file(f, driver, args.commit)
            
    driver.close()

if __name__ == "__main__":
    main()
