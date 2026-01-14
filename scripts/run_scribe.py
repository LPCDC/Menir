import sys
import argparse
import json
from pathlib import Path
from menir_core.scribe.engine import ScribeEngine

def main():
    parser = argparse.ArgumentParser(description="Menir Scribe: Text-to-Graph Proposal Generator")
    parser.add_argument("input_file", help="Path to text file (.txt, .md)")
    parser.add_argument("--type", default="fiction", help="Project type (fiction, legal, etc.)")
    parser.add_argument("--output", default="scribe_proposal.json", help="Output JSON file for review")
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Error: File not found: {input_path}")
        sys.exit(1)
        
    text = input_path.read_text(encoding="utf-8")
    
    print(f"🕵️ Scribe analyzing '{input_path.name}' (Type: {args.type})...")
    
    engine = ScribeEngine(project_type=args.type)
    result = engine.generate_proposal(text)
    
    if result["status"] == "success":
        engine.save_proposal(result["proposal"], args.output)
        print(f"✅ Proposal generated: {args.output}")
        print("⚠️  ACTION REQUIRED: Review this JSON before merging!")
    elif result["status"] == "skipped":
        print(f"🔒 Skipped: {result['reason']}")
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    main()
