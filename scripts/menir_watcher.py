import time
import os
import sys

# --- BLOCO DE AUTO-CURA (Executa ANTES de tudo) ---
try:
    import requests
    import watchdog
    from watchdog.observers.polling import PollingObserver
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("[SYSTEM]  Dependências faltando. Instalando requests e watchdog...")
    os.system("pip install requests watchdog")
    print("[SYSTEM]  Instalação concluída. Retomando...")
    import requests
    import watchdog
    from watchdog.observers.polling import PollingObserver
    from watchdog.events import FileSystemEventHandler
# ---------------------------------------------------

# Configurações
WATCH_DIR = "/app/data/inbox"
API_URL = "http://menir-app:8000/process"

class MenirHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return
        self.process_file(event.src_path)

    def on_moved(self, event):
        if event.is_directory: return
        self.process_file(event.dest_path)

    def process_file(self, filepath):
        filename = os.path.basename(filepath)
        if filename.startswith('.'): return

        print(f"\n[WATCHER]  Detectado: {filename}")
        print(f"[WATCHER]  Aguardando estabilização (2s)...")
        time.sleep(2)

        print(f"[WATCHER]  Enviando para o Cérebro (Gemini)...")
        
        try:
            with open(filepath, 'rb') as f:
                # Envia como multipart/form-data
                files = {'file': (filename, f, 'application/pdf')}
                response = requests.post(API_URL, files=files)
            
            if response.status_code == 200:
                print(f"[WATCHER]  SUCESSO! O Menir processou o arquivo.")
                try:
                    print(f"[SERVER REPLY] {response.json()}")
                except:
                    print(f"[SERVER REPLY] {response.text}")
            else:
                print(f"[WATCHER]  Erro do Servidor: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"[WATCHER]  Falha de Conexão: {str(e)}")
            print(f"[HINT] Verifique se o container menir-app está rodando na porta 8000.")

def start_watching():
    if not os.path.exists(WATCH_DIR):
        os.makedirs(WATCH_DIR, exist_ok=True)

    print(f"[WATCHER]  Menir Watcher (Neural Link v1.1).")
    print(f"[WATCHER] Alvo: {API_URL}")

    event_handler = MenirHandler()
    observer = PollingObserver()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watching()
