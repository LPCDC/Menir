#!/usr/bin/env python3
"""
Memoetic CLI for Menir — summary, voice, memes analysis from JSONL logs.
"""
import argparse
from pathlib import Path
from menir10.memoetic import extract_memoetics, summarize_voice, list_memes, DEFAULT_LOG_PATH


def main():
    parser = argparse.ArgumentParser(description="Memoetic analysis for a Menir project")
    parser.add_argument("--project", "-p", required=True, help="Project id")
    parser.add_argument(
        "--mode", "-m", choices=["summary", "voice", "memes"], default="summary"
    )
    parser.add_argument(
        "--log-file", default=str(DEFAULT_LOG_PATH), help="Path to JSONL log file"
    )
    args = parser.parse_args()
    log_path = Path(args.log_file)

    if args.mode == "summary":
        prof = extract_memoetics(args.project, log_path=log_path)
        print(f"Project: {prof.project_id}")
        print(f"Total interactions: {prof.total_interactions}")
        print("Top terms:")
        for term, freq in prof.top_terms:
            print(f"  {term}: {freq}")
        print("Sample quotes:")
        for q in prof.sample_quotes:
            print(" -", q)
    elif args.mode == "voice":
        print(summarize_voice(args.project, log_path=log_path))
    else:  # memes
        data = list_memes(args.project, log_path=log_path)
        print("Recurring terms (freq >= 3):")
        for item in data["terms"]:
            print(f"  {item['term']}: {item['freq']}")
        print("Sample quotes:")
        for q in data["sample_quotes"]:
            print(" -", q)


if __name__ == "__main__":
    main()
