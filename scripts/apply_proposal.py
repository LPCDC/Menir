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
        report = applicator.apply_proposal(data)
        
        # Save Report
        report_path = path.with_suffix(".report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"✅ Application Complete! Report saved to: {report_path}")
        print(f"   Status: {report['status'].upper()}")
        print(f"   Summary: {report['summary']}")
        
        if report['status'] != 'success':
            print("⚠️  Warnings/Errors found:")
            print(f"   Notes: {report.get('notes', [])}")
            print(f"   Orphan Scenes: {report['scene_integrity']['orphan_scenes']}")

    finally:
        applicator.close()

if __name__ == "__main__":
    main()
