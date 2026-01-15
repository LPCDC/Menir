import time, os, sys
import httpx

from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

sys.path.append("/app")

# API Config
API_URL = os.getenv("MENIR_API_URL", "http://localhost:8000")
API_TOKEN = os.getenv("MENIR_API_TOKEN", "opal_pilot_token_2025")

# Neo4j Heartbeat Class (Autonomy Feature)
import threading
from neo4j import GraphDatabase

class Heartbeat(threading.Thread):
    def __init__(self, interval=3600):
        super().__init__()
        self.interval = interval
        self.daemon = True 
        self.uri = os.getenv("NEO4J_URI", "bolt://menir-db:7687")
        self.auth = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PWD", "menir123"))

    def run(self):
        print(f"[HEARTBEAT] Started. Interval: {self.interval}s")
        while True:
            try:
                driver = GraphDatabase.driver(self.uri, auth=self.auth)
                driver.verify_connectivity()
                print("[HEARTBEAT] 🟢 Neo4j Connected")
                driver.close()
            except Exception as e:
                print(f"[HEARTBEAT] 🔴 Disconnected: {e}")
            time.sleep(self.interval)

class MenirHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return
        filename = event.src_path
        
        if filename.lower().endswith(('.pdf', '.txt')):
            print(f"[WATCHER] New File Detected: {filename}")
            self.submit_proposal(filename)

    def submit_proposal(self, filepath):
        """Submit an ingest_file proposal to the Scribe API."""
        payload = {
            "project_id": "watcher_ingest",
            "type": "ingest_file",
            "source_metadata": {
                "channel": "cli",
                "app_id": "service_watcher"
            },
            "payload": {
                "filepath": filepath,
                "status": "pending_processing"
            }
        }
        
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        try:
            # Using httpx for async/sync compatibility (sync here)
            response = httpx.post(
                f"{API_URL}/v1/scribe/proposal", 
                json=payload, 
                headers=headers,
                timeout=5.0
            )
            if response.status_code == 200:
                res_data = response.json()
                print(f"[WATCHER] 🟢 Proposal Created: {res_data.get('proposal_id')}")
            else:
                print(f"[WATCHER] 🔴 API Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[WATCHER] ❌ Connection Failed: {e}")

if __name__ == "__main__":
    path = "/app/data/inbox"
    os.makedirs(path, exist_ok=True)
    
    # Wait for API to be ready
    print("[WATCHER] Waiting for API...")
    time.sleep(5) 
    
    obs = Observer()
    handler = MenirHandler()
    obs.schedule(handler, path, recursive=False)
    obs.start()
    
    print(f"[WATCHER] Monitoring: {path}")
    print(f"[WATCHER] Target API: {API_URL}")
    
    # Start Heartbeat (Every 60 minutes = 3600s)
    beat = Heartbeat(interval=3600)
    beat.start()
    
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()
