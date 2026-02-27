import os
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestPrep")

def reset():
    # 1. Reset Files
    base = "Menir_Inbox"
    archive = os.path.join(base, "Archive")
    targets = ["Better in Manhattan"]
    
    count = 0
    if os.path.exists(archive):
        for f in os.listdir(archive):
            if any(t in f for t in targets) and f.endswith(".pdf"):
                try:
                    shutil.move(os.path.join(archive, f), os.path.join(base, f))
                    count += 1
                except Exception as e:
                    logger.warning(f"Move failed for {f}: {e}")
    
    logger.info(f"files_moved={count}")

    # 2. Purge Logs (No file deletion, just truncation or we can start fresh runner)
    # Actually, menir_runner uses basicConfig, usually printing to stderr/stdout.
    # If we want to capture file log, we should configure a FileHandler.
    # For now, we rely on the Runner's console output via the Agent's run_command tool tools.
    
if __name__ == "__main__":
    reset()
