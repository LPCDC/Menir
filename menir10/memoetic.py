"""
Menir Memoetic Layer

This module extracts narrative patterns from Menir interaction logs.
It works purely on the JSONL log file and does not depend on Neo4j.

Log schema (minimal, tolerant):
{
  "ts": "ISO8601 timestamp",
  "project_id": "itau_15220012",
  "intent_profile": "note|call|summary|boot|...",
  "content": "text of the interaction",
  "metadata": { "content": "optional content override", ... }
}
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from collections import Counter


DEFAULT_LOG_PATH = Path("logs/menir10_interactions.jsonl")


# A very small, language-agnostic stopword set (PT/EN mixed, minimal on purpose)
_STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "de", "do", "da", "das", "dos",
    "e", "ou", "em", "no", "na", "nas", "nos", "por", "pra", "para",
    "the", "and", "or", "of", "to", "in", "on", "at", "is", "are",
    "eu", "voce", "você", "que", "se", "com", "sem", "mas", "não",
}


@dataclass
class MemoeticProfile:
    project_id: str
    total_interactions: int
    top_terms: List[Tuple[str, int]]
    sample_quotes: List[str]


def _iter_interactions(
    log_path: Path,
    project_id: Optional[str] = None,
) -> Iterable[Dict[str, Any]]:
    if not log_path.exists():
        return []

    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            if project_id and data.get("project_id") != project_id:
                continue

            yield data


def _extract_text(entry: Dict[str, Any]) -> str:
    # Prefer explicit content; fall back to metadata.content
    content = entry.get("content")
    if not content:
        meta = entry.get("metadata") or {}
        content = meta.get("content", "")
    return str(content)


def _tokenize(text: str) -> List[str]:
    # Simple word tokenizer, case-folded, strip non-alpha
    tokens = re.split(r"[^\wÀ-ÿ]+", text.lower())
    cleaned: List[str] = []
    for t in tokens:
        if not t:
            continue
        # ignore mostly numeric tokens
        if t.isdigit():
            continue
        if t in _STOPWORDS:
            continue
        cleaned.append(t)
    return cleaned


def extract_memoetics(
    project_id: str,
    log_path: Path = DEFAULT_LOG_PATH,
    max_interactions: int = 500,
    top_n_terms: int = 20,
) -> MemoeticProfile:
    """
    Build a MemoeticProfile for a given project_id.

    It:
    - loads interactions from the JSONL log
    - tokenizes text content
    - counts term frequencies
    - keeps a few sample quotes (longer snippets)
    """
    entries: List[Dict[str, Any]] = []
    term_counter: Counter[str] = Counter()
    quotes: List[str] = []

    for idx, entry in enumerate(_iter_interactions(log_path, project_id)):
        if idx >= max_interactions:
            break
        entries.append(entry)
        text = _extract_text(entry)
        if not text:
            continue

        tokens = _tokenize(text)
        term_counter.update(tokens)

        # keep sample quotes that are not too short
        if len(text) >= 40:
            quotes.append(text.strip())

    top_terms = term_counter.most_common(top_n_terms)
    # take up to 5 sample quotes
    sample_quotes = quotes[:5]

    return MemoeticProfile(
        project_id=project_id,
        total_interactions=len(entries),
        top_terms=top_terms,
        sample_quotes=sample_quotes,
    )


def summarize_voice(
    project_id: str,
    log_path: Path = DEFAULT_LOG_PATH,
) -> str:
    """
    Produce a human-readable description of the project's narrative "voice".
    This is deterministic and does not call any LLM.
    """
    profile = extract_memoetics(project_id, log_path=log_path)

    if profile.total_interactions == 0:
        return (
            f"Project '{project_id}' has no memoetic footprint yet. "
            f"No interactions were found in {log_path}."
        )

    dominant_terms = [t for t, _ in profile.top_terms[:5]]
    total_terms = sum(freq for _, freq in profile.top_terms) or 1

    # crude signals
    long_quotes = len([q for q in profile.sample_quotes if len(q) > 120])
    short_quotes = len(profile.sample_quotes) - long_quotes

    style_parts: List[str] = []
    style_parts.append(
        f"Project '{profile.project_id}' currently has "
        f"{profile.total_interactions} logged interactions."
    )

    if dominant_terms:
        style_parts.append(
            "Its vocabulary tends to revolve around: "
            + ", ".join(dominant_terms) + "."
        )

    if long_quotes and short_quotes:
        style_parts.append(
            "It alternates between short notes and longer reflective passages."
        )
    elif long_quotes:
        style_parts.append(
            "It favours longer, more reflective entries rather than short notes."
        )
    elif short_quotes:
        style_parts.append(
            "It is mostly composed of short, direct notes."
        )

    # Ratio of unique terms to total terms as a crude proxy for lexical variety
    unique_terms = len(profile.top_terms)
    variety_ratio = unique_terms / float(total_terms)
    if variety_ratio > 0.4:
        style_parts.append(
            "The language shows high lexical variety, suggesting exploratory thinking."
        )
    elif variety_ratio > 0.2:
        style_parts.append(
            "The language balances repetition and variety, suggesting focused iteration."
        )
    else:
        style_parts.append(
            "The language is highly repetitive, pointing to a narrow, intense theme."
        )

    return " ".join(style_parts)


def list_memes(
    project_id: str,
    log_path: Path = DEFAULT_LOG_PATH,
    max_interactions: int = 500,
    min_freq: int = 3,
) -> Dict[str, Any]:
    """
    Return a structured view of recurring expressions ("memes")
    in the textual history of a project.

    Output:
    {
      "project_id": "...",
      "total_interactions": N,
      "terms": [ {"term": "itau", "freq": 10}, ... ],
      "sample_quotes": [ ... ]
    }
    """
    profile = extract_memoetics(
        project_id=project_id,
        log_path=log_path,
        max_interactions=max_interactions,
    )

    filtered_terms = [
        {"term": term, "freq": freq}
        for term, freq in profile.top_terms
        if freq >= min_freq
    ]

    return {
        "project_id": profile.project_id,
        "total_interactions": profile.total_interactions,
        "terms": filtered_terms,
        "sample_quotes": profile.sample_quotes,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Inspect memoetic profile for a given Menir project."
    )
    parser.add_argument("--project", "-p", required=True, help="Project id")
    parser.add_argument(
        "--mode",
        "-m",
        choices=["summary", "voice", "memes"],
        default="summary",
        help="Output mode",
    )
    parser.add_argument(
        "--log-file",
        default=str(DEFAULT_LOG_PATH),
        help="Path to menir10_interactions.jsonl",
    )

    args = parser.parse_args()
    log_path = Path(args.log_file)

    if args.mode == "summary":
        profile = extract_memoetics(args.project, log_path=log_path)
        print(f"Project: {profile.project_id}")
        print(f"Total interactions: {profile.total_interactions}")
        print("Top terms:")
        for term, freq in profile.top_terms:
            print(f"  - {term}: {freq}")
        if profile.sample_quotes:
            print("\nSample quotes:")
            for q in profile.sample_quotes:
                print(f"- {q}")
    elif args.mode == "voice":
        print(summarize_voice(args.project, log_path=log_path))
    else:  # memes
        data = list_memes(args.project, log_path=log_path)
        print(f"Project: {data['project_id']}")
        print(f"Total interactions: {data['total_interactions']}")
        print("Recurring terms (freq >= 3):")
        for item in data["terms"]:
            print(f"  - {item['term']}: {item['freq']}")
        if data["sample_quotes"]:
            print("\nSample quotes:")
            for q in data["sample_quotes"]:
                print(f"- {q}")
