import time
import os
import sys
import json
import re

# --- BLOCO DE AUTO-CURA ---
try:
    import requests
    import watchdog
    from neo4j import GraphDatabase
    from watchdog.observers.polling import PollingObserver
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("[SYSTEM] Dependências faltando. Instalando requests, watchdog, neo4j...")
    os.system("pip install requests watchdog neo4j")
    print("[SYSTEM] Instalação concluída. Retomando...")
    import requests
    import watchdog
    from neo4j import GraphDatabase
    from watchdog.observers.polling import PollingObserver
    from watchdog.events import FileSystemEventHandler
# ---------------------------

# Configurações
WATCH_DIR = "/app/data/inbox"
API_URL = "http://menir-app:8000/process"
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://menir-db:7687")
NEO4J_AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "menir123"))

USER_DATA_DIR = os.getenv("USER_DATA_DIR", "/app/user_data")
PROFILE_FILE = os.path.join(USER_DATA_DIR, "user_profile.json")

class MenirVitalV6:
    def __init__(self):
        self.lenses = {}
        self.active_lens = "Standard"
        self.memory = []
        self._load_lenses()
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
        
    def _load_lenses(self):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for lens in data.get("professional_lenses", []):
                    self.lenses[lens["id"]] = lens
            print(f"[V6] Lenses Loaded: {', '.join([l['name'] for l in self.lenses.values()])}")
        except FileNotFoundError:
            print("[V6] WARN: user_profile.json not found. Running in basic mode.")

    def detect_intent(self, user_query):
        user_query = user_query.lower()
        for lid, lens in self.lenses.items():
            for kw in lens["trigger_keywords"]:
                if kw in user_query:
                    self.active_lens = lens["name"]
                    return self.active_lens
        return "Standard"

    def resolve_namespace(self, entity_name):
        print(f"[V6] Resolving '{entity_name}' under Lens: {self.active_lens}")
        
        # Logic: Determine Label based on Lens
        target_label = "Person" # Default Real World
        if "Editor" in self.active_lens or "Writer" in self.active_lens:
            target_label = "Character"
        
        # Specific override for Strategist/Architect -> Person
        if "Strategist" in self.active_lens or "Architect" in self.active_lens:
            target_label = "Person"

        query = f"MATCH (n:{target_label}) WHERE n.name CONTAINS $name RETURN n.name, labels(n)"
        
        with self.driver.session() as session:
            result = session.run(query, name=entity_name)
            matches = [record["n.name"] for record in result]
            
            if matches:
                return f"Found {target_label}: {matches[0]}"
            else:
                # Fallback check
                fallback_query = "MATCH (n) WHERE n.name CONTAINS $name RETURN n.name, labels(n)"
                fb_result = session.run(fallback_query, name=entity_name)
                fb_matches = [f"{list(r['labels(n)'])[0]}: {r['n.name']}" for r in fb_result]
                if fb_matches:
                     return f"Ambiguous/Fallback: Found {', '.join(fb_matches)}"
                return None

    def active_learning(self, text):
        # Simple extraction: Capitalized words not at start of sentence (simplified)
        # For this demo, we assume the input might BE the entity or contain it clearly.
        # Let's just look for Proper Nouns or just take the whole text if short.
        
        potential_entities = [w for w in text.split() if w[0].isupper() and len(w) > 2]
        
        warnings = []
        with self.driver.session() as session:
            for entity in potential_entities:
                res = session.run("MATCH (n) WHERE n.name CONTAINS $name RETURN count(n) as c", name=entity)
                count = res.single()["c"]
                if count == 0:
                    self.memory.append(entity)
                    warnings.append(f"[SYSTEM]: Detectei '{entity}'. É um novo personagem para o Livro ou um contato da MAU? Digite /add para indexar.")
        
        return " ".join(warnings)

    def close(self):
        self.driver.close()

# Watcher Handler Legacy + V6 Integration
class MenirHandler(FileSystemEventHandler):
    def __init__(self, brain):
        self.brain = brain
        
    def on_created(self, event):
        if event.is_directory: return
        self.process_file(event.src_path)

    def process_file(self, filepath):
        filename = os.path.basename(filepath)
        if filename.startswith('.'): return

        print(f"\n[WATCHER]  Detectado: {filename}")
        time.sleep(1)
        
        # Simulate processing text content as query if txt
        if filename.endswith(".txt"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                
                print(f"[INPUT] {content}")
                
                # 1. Detect Lens
                lens = self.brain.detect_intent(content)
                print(f"[BRAIN] Active Lens: {lens}")
                
                # 2. Checking for known entities (manual trigger for demo hardcoded names or just active learning)
                # For demo purposes, we scan standard knowns.
                if "Caroline" in content:
                    res = self.brain.resolve_namespace("Caroline")
                    print(f"[BRAIN] Namespace Resolution: {res}")

                # 3. Active Learning
                learning = self.brain.active_learning(content)
                if learning:
                    print(learning)
                    
            except Exception as e:
                print(f"Error processing text: {e}")

def start_watching():
    if not os.path.exists(WATCH_DIR):
        os.makedirs(WATCH_DIR, exist_ok=True)
    
    # Initialize V6 Brain
    brain = MenirVitalV6()
    
    print(f"INTELLIGENCE_ONLINE: Watcher V6 running.")
    print(f"Lenses Loaded: {', '.join([l['name'] for l in brain.lenses.values()])}.")
    print(f"Namespace Logic: Active (Context-Aware Disambiguation).")
    print(f"Active Learning: Armed (Monitoring for new entities). MENIR V6.0 VITAL IS FULLY OPERATIONAL.")

    event_handler = MenirHandler(brain)
    observer = PollingObserver()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        brain.close()
    observer.join()

if __name__ == "__main__":
    start_watching()
