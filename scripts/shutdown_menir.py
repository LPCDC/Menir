import sys
import os
import logging
from datetime import datetime

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Import Backup Logic
try:
    import backup_routine
except ImportError:
    print("❌ Critical: scripts/backup_routine.py not found.")
    sys.exit(1)

# Configure Log
logging.basicConfig(level=logging.INFO, format='%(message)s')

def main():
    print("\n🛑 SHUTDOWN SEQUENCE INITIATED")
    print("==============================")
    
    # 1. Run Backup
    print("\n[1/2] Creating System Backup...")
    try:
        backup_routine.perform_backup()
        print("✅ Backup Verified.")
    except Exception as e:
        print(f"❌ BACKUP FAILED: {e}")
        print("⚠️  Shutdown aborted to protect data.")
        sys.exit(1)

    # 2. Logic Shutdown (Promote Tasks, etc) - Placeholder for now
    print("\n[2/2] Finalizing Session...")
    # TODO: Restaurar lógica de Task Promotion se/quando recuperada
    
    print("\n------------------------------")
    print("👋 MENIR SYSTEM HALTED SAFELY.")
    print("   Data is secured in /backups")
    print("------------------------------\n")

if __name__ == "__main__":
    main()
