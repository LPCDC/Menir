
import os
import shutil
import logging

INBOX = "Menir_Inbox"
QUARANTINE = "Menir_Inbox/Quarantine"

logging.basicConfig(level=logging.INFO)

print("🚑 Restoring Quarantined Files...")

if not os.path.exists(QUARANTINE):
    print("No Quarantine folder.")
    exit()

files = os.listdir(QUARANTINE)

for f in files:
    if f.startswith("debug_"): continue # Skip debug copies
    
    src = os.path.join(QUARANTINE, f)
    
    # Remove .ERROR suffix if present
    original_name = f.replace(".ERROR", "").replace(".AUDIT_FAIL", "")
    dst = os.path.join(INBOX, original_name)
    
    try:
        shutil.move(src, dst)
        print(f"✅ Restored: {original_name}")
    except Exception as e:
        print(f"❌ Failed {f}: {e}")

print("Done.")
