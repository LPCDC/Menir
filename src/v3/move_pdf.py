import shutil
import os
import logging

logging.basicConfig(level=logging.INFO)

src_dir = "Menir_Inbox/Archive"
dst_dir = "Menir_Inbox"
filename = "“Better in Manhattan” 1°cap Débora Vezzoli.pdf"

src = os.path.join(src_dir, filename)
dst = os.path.join(dst_dir, filename)

if os.path.exists(src):
    try:
        shutil.move(src, dst)
        logging.info(f"Moved {src} -> {dst}")
    except Exception as e:
        logging.error(f"Move failed: {e}")
else:
    logging.warning(f"Source not found: {src}")
    # Try finding it
    for root, dirs, files in os.walk("Menir_Inbox"):
        for f in files:
            if "Better in Manhattan" in f:
                logging.info(f"Found candidate: {os.path.join(root, f)}")
