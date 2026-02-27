
import os
import shutil

ARCHIVE_DIR = "Menir_Archive"
INBOX_DIR = "Menir_Inbox"

def replay():
    if not os.path.exists(ARCHIVE_DIR):
        print(f"Archive not found: {ARCHIVE_DIR}")
        return

    if not os.path.exists(INBOX_DIR):
        os.makedirs(INBOX_DIR)

    files = [f for f in os.listdir(ARCHIVE_DIR) if f.lower().endswith('.pdf')]
    
    if not files:
        print("No PDFs found in Archive.")
        return

    print(f"Replaying {len(files)} files from {ARCHIVE_DIR} to {INBOX_DIR}...")
    
    for f in files:
        src = os.path.join(ARCHIVE_DIR, f)
        dst = os.path.join(INBOX_DIR, f)
        try:
            shutil.move(src, dst)
            print(f"Moved: {f}")
        except Exception as e:
            print(f"Failed to move {f}: {e}")

if __name__ == "__main__":
    replay()
