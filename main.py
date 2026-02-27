import sys
import os
import time

# Adiciona a pasta src ao caminho do sistema
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# --- AQUI ESTAVA O ERRO DO 'HUB' ---
# Nós importamos e damos o apelido (alias) 'hub' explicitamente.
try:
    from src import menir_ui
    from src import drive_hub as hub 
except ImportError as e:
    print(f"FATAL ERROR: Falha na importação. {e}")
    # Mock para teste se falhar importação
    class MockHub:
        def authenticate_google(self): pass
    hub = MockHub()

def main():
    print("--- MENIR VITAL SYSTEM v6.0 ---")
    
    # 1. Autenticação (O Polvo)
    print("1. Connecting to Drive Hub...")
    try:
        hub.authenticate_google()
        print("   [OK] Drive Authenticated.")
    except Exception as e:
        print(f"   [WARN] Drive Offline: {e}")

    # 2. Interface (O HUD)
    print("2. Launching UI...")
    time.sleep(1) # Pausa dramática para ler o log
    try:
        menir_ui.run_shell()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Menir OS closed.")

if __name__ == "__main__":
    main()
