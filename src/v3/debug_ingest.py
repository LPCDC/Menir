
import os
import shutil
import logging
import traceback
from dotenv import load_dotenv

# Force Env Load
load_dotenv(override=True)

from src.v3.menir_bridge import MenirBridge
from src.v3.menir_intel import MenirIntel
from src.v3.menir_audit import MenirAudit
from src.v3.menir_runner import process_file

# Setup Console Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DebugIngest")

QUARANTINE_DIR = "Menir_Inbox/Quarantine"
DEBUG_FILE = "debug_sample.pdf"

def debug():
    print("🐞 STARTING DEBUG SESSION...")
    
    # 1. Find a file
    files = [f for f in os.listdir(QUARANTINE_DIR) if f.endswith('.ERROR')]
    if not files:
        print("No files in Quarantine to debug.")
        return

    target = files[0]
    src_path = os.path.join(QUARANTINE_DIR, target)
    dst_path = os.path.join(os.getcwd(), DEBUG_FILE)
    
    print(f"🔬 Analyzing: {target}")
    shutil.copy(src_path, dst_path) # Copy to root as .pdf
    
    # 2. Init Components
    try:
        bridge = MenirBridge()
        intel = MenirIntel(os.getenv("GOOGLE_API_KEY"))
        audit = MenirAudit(
            os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON"),
            os.getenv("MENIR_AUDIT_SHEET_ID"),
            "Audit_Debug"
        )
        audit._connect() # Quick check
        
        # 3. Run Process
        print(">>> EXECUTING PROCESS_FILE <<<")
        process_file(dst_path, bridge, intel, audit)
        print(">>> SUCCESS <<<")
        
    except Exception as e:
        print("\n❌ CRASH REPORT:")
        traceback.print_exc()
    finally:
        if 'bridge' in locals(): bridge.close()
        # Cleanup
        if os.path.exists(dst_path):
            os.remove(dst_path)

if __name__ == "__main__":
    debug()
