import time, os, sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
sys.path.append("/app")

try:
    from menir_core.ingest.pdf_adapter import extract_text_from_pdf
except ImportError:
    extract_text_from_pdf = None

class MenirHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return
        filename = event.src_path
        if filename.lower().endswith('.pdf'):
            print(f"[WATCHER] PDF Detectado: {filename}")
            if extract_text_from_pdf:
                data = extract_text_from_pdf(filename)
                if data: print(f"[WATCHER] Sucesso! Lido {len(data['full_text'])} chars.")

if __name__ == "__main__":
    path = "/app/data/inbox"
    os.makedirs(path, exist_ok=True)
    obs = Observer()
    obs.schedule(MenirHandler(), path, recursive=False)
    obs.start()
    print("[WATCHER] Monitorando: " + path)
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()
