
import os
import shutil

ARCHIVE = "Menir_Inbox/Archive"
INBOX = "Menir_Inbox"
FILE = "TIVOLI-MEMORIAL_sdfd - Copy.pdf"

src = os.path.join(ARCHIVE, FILE)
dst = os.path.join(INBOX, FILE)

if os.path.exists(src):
    shutil.move(src, dst)
    print(f"Moved {FILE} to Inbox.")
else:
    print("File not found in Archive.")
