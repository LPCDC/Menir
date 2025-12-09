import argparse
import json
import sys
from pathlib import Path
from menir_core.scribe.applicator import ScribeApplicator

def main():
    parser = argparse.ArgumentParser(description="Menir Scribe: Apply Proposal")
    parser.add_argument("proposal_file", help="Path to JSON proposal file")
    
    args = parser.parse_args()
    path = Path(args.proposal_file)
    
    if not path.exists():
        print(f"❌ File not found: {path}")
        sys.exit(1)
        
    print(f"📖 Reading proposal: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    
    # Simple Confirmation
    print(f"Found {len(data.get('nodes', []))} nodes, {len(data.get('relationships', []))} rels.")
    confirm = input("⚠️  Are you sure you want to write this to Neo4j? (yes/no): ")
    
    if confirm.lower() != "yes":
        print("🚫 Aborted.")
        sys.exit(0)
        
    applicator = ScribeApplicator()
    try:
        stats = applicator.apply_proposal(data)
        print("✅ Application Complete!")
        print(f"   Nodes processed: {stats['nodes_created']}")
        print(f"   Rels processed: {stats['relationships_created']}")
        if stats['errors']:
            print(f"   ❌ Errors: {len(stats['errors'])}")
            for err in stats['errors']:
                print(f"      - {err}")
    finally:
        applicator.close()

if __name__ == "__main__":
    main()
