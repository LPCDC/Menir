import os
import shutil
import logging
from src.v3.menir_bridge import MenirBridge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmokeTestPrep")

FILENAME = "“Better in Manhattan” 1°cap Débora Vezzoli.pdf"
ARCHIVE_PATH = os.path.join("Menir_Inbox", "Archive", FILENAME)
INBOX_PATH = os.path.join("Menir_Inbox", FILENAME)

def reset_state():
    # 1. Delete from Graph
    bridge = MenirBridge()
    with bridge.driver.session() as session:
        logger.info(f"Deleting Document node for: {FILENAME}")
        query = "MATCH (d:Document {filename: $f}) DETACH DELETE d RETURN count(d) as c"
        res = session.run(query, f=FILENAME)
        c = res.single()['c']
        logger.info(f"Deleted {c} Document Node(s).")
    bridge.close()

    # 2. Move File from Archive to Inbox
    if os.path.exists(ARCHIVE_PATH):
        logger.info(f"Moving {FILENAME} back to Inbox...")
        shutil.move(ARCHIVE_PATH, INBOX_PATH)
        logger.info("File Restored.")
    else:
        logger.warning(f"File not found in Archive: {ARCHIVE_PATH}")
        # Check if it's already in inbox?
        if os.path.exists(INBOX_PATH):
             logger.info("File is already in Inbox.")

if __name__ == "__main__":
    reset_state()
