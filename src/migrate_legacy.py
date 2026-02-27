import os
import shutil
import glob
from pathlib import Path

LEGACY_PATH = Path("legacy_backup/data")
INBOX_PATH = Path("data/inbox")

def migrate():
    # Use absolute path if exists, else try relative to current dir check
    if not LEGACY_PATH.exists():
        print(f"Legacy path not found: {LEGACY_PATH}")
        # Try finding data in current dir recursively or assume provided path is correct
        # Fallback to local data dir for safety if user meant local
        return

    INBOX_PATH.mkdir(parents=True, exist_ok=True)
    
    extensions = ['*.pdf', '*.txt']
    files_to_move = []
    
    for ext in extensions:
        files_to_move.extend(LEGACY_PATH.glob(f"**/{ext}"))
        
    print(f"Found {len(files_to_move)} files to migrate.")
    
    for f in files_to_move:
        # Avoid moving files that are already in inbox or proposals
        if "inbox" in str(f) or "proposals" in str(f):
            continue
            
        dest = INBOX_PATH / f.name
        try:
            shutil.copy2(f, dest)
            print(f"[MIGRATE] Copied {f.name} -> Inbox")
        except Exception as e:
            print(f"[ERROR] Failed to copy {f.name}: {e}")

if __name__ == "__main__":
    migrate()
