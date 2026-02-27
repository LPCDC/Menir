import os
from pypdf import PdfReader

inbox_dir = "./Menir_Inbox"
files = [f for f in os.listdir(inbox_dir) if f.endswith(".pdf")]

print(f"Found {len(files)} PDFs in {inbox_dir}")

for f in files[:3]:
    path = os.path.join(inbox_dir, f)
    try:
        reader = PdfReader(path)
        meta = reader.metadata
        print(f"\n--- {f} ---")
        if meta:
            print(f"Title: {meta.title}")
            print(f"Author: {meta.author}")
            print(f"Producer: {meta.producer}")
            print(f"CreationDate: {meta.creation_date}")
        else:
            print("NO METADATA FOUND")
    except Exception as e:
        print(f"Error reading {f}: {e}")
