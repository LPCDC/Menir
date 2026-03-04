"""
Menir Core V5.1 - Functional Healthcheck Probe
A tactical script built for Docker's HEALTHCHECK instruction.
It goes beyond simple pinging: it measures Neo4j transaction latency
and interrogates the Synapse Control Plane to ensure the Event Loop
is not suffering from Deadlocks or severe Semaphore starvation.
"""
import sys
import time
import requests
import os
from dotenv import load_dotenv
from src.v3.meta_cognition import MenirOntologyManager

def check_synapse_health():
    """Verifica se o Watchdog e o Event Loop do Python estão respirando."""
    try:
        # A API Rest responde super rápido se o Event Loop estiver livre
        start = time.time()
        resp = requests.get("http://127.0.0.1:8080/status", timeout=3)
        latency = (time.time() - start) * 1000
        
        if resp.status_code == 200:
            data = resp.json()
            queue_size = data.get("command_queue_size", 0)
            if queue_size > 50:
                 print(f"WARNING: Mesh Queue is clogged ({queue_size} items).")
                 return False
            
            print(f"Synapse OK - Latency {latency:.1f}ms")
            return True
        return False
    except Exception as e:
        print(f"Synapse CRITICAL FAIL: {e}")
        return False

def check_neo4j_latency():
    """Mede a latência de I/O do Pool de Conexões do Neo4j."""
    load_dotenv(override=True)
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    pwd = os.getenv("NEO4J_PASSWORD") or os.getenv("NEO4J_PWD")
    db = os.getenv("NEO4J_DB", "neo4j")
    
    om = MenirOntologyManager(uri, (user, pwd), db_name=db)
    try:
        start = time.time()
        with om.driver.session() as session:
            session.run("RETURN 1")
        latency = (time.time() - start) * 1000
        
        print(f"Neo4j OK - Latency {latency:.1f}ms")
        
        # O Padrão Enterprise: Se o Grafo leva mais de 2000ms só para o Handshake,
        # O pool de conexões está estourado ou o NAS falhou I/O.
        if latency > 2000:
            print("CRITICAL: Neo4j Write-Lock/Latency exceeding 2000ms safety limit.")
            return False
            
        return True
    except Exception as e:
        print(f"Neo4j CRITICAL FAIL: {e}")
        return False

if __name__ == "__main__":
    neo4j_ok = check_neo4j_latency()
    synapse_ok = check_synapse_health()
    
    # Se ambos falharem ou um vital falhar, o Docker reinicia o Menir.
    if neo4j_ok and synapse_ok:
        sys.exit(0) # Healthy
    else:
        sys.exit(1) # Unhealthy
