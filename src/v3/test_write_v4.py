
import os
import logging
from src.v3.menir_bridge import MenirBridge
from src.v3.schema import Document

logging.basicConfig(level=logging.INFO)

print("🧪 Testing Direct DB Write...")

try:
    bridge = MenirBridge()
    doc = Document(
        filename="TEST_WRITE_V4.pdf",
        sha256="0000000000000000000000000000000000000000000000000000000000000001",
        project="Menir_Test",
        status="processed"
    )
    print(f"Attempting to merge: {doc}")
    bridge.merge_node(doc)
    print("✅ Merge call finished without error.")
    
    # Verify
    if bridge.check_document_exists(doc.sha256):
         print("✅ Verified: Node exists in DB.")
    else:
         print("❌ Verified: Node NOT found in DB after write.")

    bridge.close()
except Exception as e:
    print(f"❌ CRASH: {e}")
