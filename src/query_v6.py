import sys
import os
sys.path.append("/app/scripts")
from menir_watcher import MenirVitalV6

def process_query(text):
    print(f"🧠 PROCESSING INPUT: \"{text}\"")
    brain = MenirVitalV6()
    
    # 1. Detect Lens
    lens = brain.detect_intent(text)
    print(f"\n[1] LENS SHIFT: {lens}")
    print(f"    (Triggered by keywords in input)")

    # 2. Entity Check (Simulated NER: 'Ricardo', 'Tivoli')
    # In a real app, an LLM/Spacy would extract these. We manually test 'Ricardo' and 'Tivoli' for this demo.
    entities = ["Ricardo", "Tivoli"]
    
    print("\n[2] ENTITY RESOLUTION:")
    for ent in entities:
        # Check graph
        res = brain.resolve_namespace(ent)
        if res:
            print(f"    - '{ent}': {res}")
        else:
            print(f"    - '{ent}': Not found in Graph.")

    # 3. Active Learning Trigger
    print("\n[3] ACTIVE LEARNING:")
    # We pass the full text to the active learning module
    learning = brain.active_learning(text)
    if learning:
        print(f"    {learning}")
    else:
        print("    (No new entities detected)")

    print("\n[SYSTEM STATE]: READY")
    brain.close()

if __name__ == "__main__":
    process_query("O Ricardo da construtora está pedindo as plantas do Tivoli.")
