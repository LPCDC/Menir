"""
Menir Core V5.1 - Incremental Graph Backup (Chronos)
A low-impedance script to snapshot the latest mutated nodes (Provenance/Audit)
and export them safely. Designed to run as a CronJob via Docker or system level.
"""
import os
import sys
import json
import logging
import time
from datetime import datetime

# Adjust module path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.v3.meta_cognition import MenirOntologyManager

logger = logging.getLogger("GraphBackup")

from dotenv import load_dotenv

def export_mutations_snapshot():
    start = time.time()
    
    # Load Credentials
    load_dotenv()
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD", "password")
    
    om = MenirOntologyManager(uri=uri, auth=(user, pwd))
    
    # Busca apenas eventos de mutação e as faturas atreladas nas últimas 24h
    query = """
    MATCH (e:Event)-[:AFFECTED]->(i:Invoice)
    WHERE e.timestamp >= datetime() - duration({days: 1})
    RETURN e.action as action, 
           e.agent as agent, 
           e.timestamp as time, 
           i.file_hash as invoice_hash, 
           i.total_amount as amount,
           labels(i) as labels
    """
    
    export_dir = "Menir_Archive/Snapshots"
    os.makedirs(export_dir, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(export_dir, f"menir_mutations_{today}.json")
    
    try:
        with om.driver.session() as session:
            result = session.run(query)
            data = [record.data() for record in result]
            
        # O output do Neo4j dateTime types precisa ser stringificado
        def serialize_neo4j(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return str(obj)
            
        with open(filepath, 'w') as f:
            json.dump(data, f, default=serialize_neo4j, indent=2)
            
        logger.info(f"💾 Snapshot de Baixa Impedância gerado em {filepath} ({len(data)} mutações salvos em {(time.time()-start)*1000:.1f}ms).")
    except Exception as e:
        logger.error(f"❌ Falha no Backup Incremental: {e}")

if __name__ == "__main__":
    import time
    export_mutations_snapshot()
