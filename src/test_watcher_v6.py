import sys
import os
import time

# Ensure we can import the watcher
sys.path.append("/app/scripts")
try:
    from menir_watcher import MenirVitalV6
except ImportError:
    print("FAILED to import MenirVitalV6 from menir_watcher.py")
    sys.exit(1)

def test_watcher():
    print("🧪 INITIALIZING V6 BRAIN...")
    brain = MenirVitalV6()
    
    # 1. Test Lens Detection
    print("\n[TEST 1] Lens Detection")
    scenarios = [
        ("Review Tivoli architecture", "Strategic Consultant (MAU/Otani)"),
        ("Fix this python bug in the code", "Product Architect (Menir)"),
        ("Edit chapter 1 of the book", "Senior Editor (Jornalista/Copywriter)"),
        ("Hello world", "Standard")
    ]
    
    for query, expected in scenarios:
        lens = brain.detect_intent(query)
        status = "✅" if lens == expected else f"❌ (Got: {lens})"
        print(f"'{query}' -> {expected} : {status}")

    # 2. Test Namespace Resolution
    print("\n[TEST 2] Namespace Resolution")
    # Determine what 'Caroline' resolves to under different lenses
    
    # Strategist -> Person
    brain.active_lens = "Strategic Consultant (MAU/Otani)"
    res_strat = brain.resolve_namespace("Caroline")
    print(f"Lens: Strategist -> {res_strat}")
    
    # Editor -> Character
    brain.active_lens = "Senior Editor (Jornalista/Copywriter)"
    res_edit = brain.resolve_namespace("Caroline")
    print(f"Lens: Editor -> {res_edit}")

    # 3. Test Active Learning
    print("\n[TEST 3] Active Learning")
    unknown_text = "Who is Vecna? I think he knows Eleven."
    learning = brain.active_learning(unknown_text)
    print(f"Input: '{unknown_text}'")
    print(f"Output: {learning}")

    brain.close()

if __name__ == "__main__":
    test_watcher()
