import sys
import os
from pathlib import Path
sys.path.append("/app")

from menir_core.ingest.extractor import MenirExtractor

def check():
    print("Initializing Extractor...")
    extractor = MenirExtractor()
    
    text = "Menir is a project using Gemini for AI."
    print(f"Testing Extraction on: '{text}'")
    
    result = extractor.extract_knowledge(text)
    print("Result:", result)
    
    if "error" in result:
        print("FAIL: API Key likely invalid/missing.")
        sys.exit(1)
    
    print("SUCCESS: JSON received.")

if __name__ == "__main__":
    check()
