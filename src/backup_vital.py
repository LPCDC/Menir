import json
import os
from neo4j import GraphDatabase
from datetime import datetime

# Configuration
URI = os.getenv("NEO4J_URI", "bolt://menir-db:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "menir123"))
BACKUP_FILE = "backups/vital_state_v5.json"

def serialize(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

def backup_graph():
    print(f"🔌 Connecting to {URI}...")
    driver = GraphDatabase.driver(URI, auth=AUTH)
    
    data = {"nodes": [], "relationships": [], "meta": {"timestamp": datetime.now().isoformat(), "version": "v5.0"}}
    
    with driver.session() as session:
        # 1. Export Nodes
        print("📦 Exporting Nodes...")
        result = session.run("MATCH (n) RETURN n, labels(n) as labels, elementId(n) as id")
        for record in result:
            node = record["n"]
            data["nodes"].append({
                "id": record["id"],
                "labels": record["labels"],
                "properties": dict(node)
            })
            
        # 2. Export Relationships
        print("🔗 Exporting Relationships...")
        result = session.run("MATCH ()-[r]->() RETURN r, type(r) as type, elementId(startNode(r)) as start, elementId(endNode(r)) as end, elementId(r) as id")
        for record in result:
            rel = record["r"]
            data["relationships"].append({
                "id": record["id"],
                "type": record["type"],
                "start": record["start"],
                "end": record["end"],
                "properties": dict(rel)
            })
            
    driver.close()
    
    # 3. Save to File
    print(f"💾 Saving to {BACKUP_FILE}...")
    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=serialize)
        
    print(f"✅ Backup Complete. Nodes: {len(data['nodes'])}, Relationships: {len(data['relationships'])}")

if __name__ == "__main__":
    backup_graph()
