# Menir Memoetic Layer Guide

## Overview

The **Memoetic Layer** is a narrative pattern extraction and analysis system designed for the Menir platform. It analyzes interaction logs to identify recurring linguistic patterns, thematic clusters, and the distinctive "voice" of a project's narrative history.

Rather than relying on heavyweight LLM-based summarization, the memoetic layer uses deterministic, linguistic heuristics to extract meaningful patterns from JSONL-formatted interaction logs.

## Core Concepts

### Memes
In the context of Menir, a **meme** is any recurring linguistic or conceptual unit that appears across interactions. This includes:
- **Terms**: High-frequency words or phrases that persist in a project's vocabulary
- **Patterns**: Structural or thematic sequences that characterize the project's thinking
- **Quotes**: Representative snippets that exemplify the project's voice

### Voice
A project's **voice** is a computed, deterministic summary of its narrative characteristics. It reflects:
- Vocabulary preferences (what terms dominate)
- Stylistic traits (long-form reflection vs. short notes)
- Lexical variety (repetitive vs. exploratory language)

### MemoeticProfile
A data structure containing:
- `project_id`: Identifier for the project
- `total_interactions`: Count of logged interactions for the project
- `top_terms`: List of (term, frequency) tuples ranked by occurrence
- `sample_quotes`: Representative text snippets from the log

## Usage

### Python API

#### Extract a Memoetic Profile
```python
from menir10.memoetic import extract_memoetics
from pathlib import Path

profile = extract_memoetics(
    project_id="itau_15220012",
    log_path=Path("logs/menir10_interactions.jsonl"),
    max_interactions=500,
    top_n_terms=20
)

print(f"Project: {profile.project_id}")
print(f"Total interactions: {profile.total_interactions}")
print(f"Top terms: {profile.top_terms}")
print(f"Sample quotes: {profile.sample_quotes}")
```

#### Summarize a Project's Voice
```python
from menir10.memoetic import summarize_voice

text = summarize_voice(
    project_id="itau_15220012",
    log_path=Path("logs/menir10_interactions.jsonl")
)
print(text)
```

This produces a human-readable, deterministic summary like:
> Project 'itau_15220012' currently has 247 logged interactions. Its vocabulary tends to revolve around: itau, credito, risco, garantia, contrato. It alternates between short notes and longer reflective passages. The language shows high lexical variety, suggesting exploratory thinking.

#### List Recurring Memes
```python
from menir10.memoetic import list_memes

data = list_memes(
    project_id="itau_15220012",
    log_path=Path("logs/menir10_interactions.jsonl"),
    min_freq=3
)

print(f"Recurring terms (freq >= 3):")
for item in data["terms"]:
    print(f"  - {item['term']}: {item['freq']}")
```

Output structure:
```json
{
  "project_id": "itau_15220012",
  "total_interactions": 247,
  "terms": [
    {"term": "itau", "freq": 45},
    {"term": "credito", "freq": 38},
    {"term": "risco", "freq": 31}
  ],
  "sample_quotes": [
    "Reunião com Itaú, discutir proposta de crédito com garantia.",
    "..."
  ]
}
```

### Command-Line Interface

The memoetic module includes a CLI for quick analysis:

```bash
# Summarize profile for a project
python -m menir10.memoetic_cli --project itau_15220012 --mode summary

# Get voice description
python -m menir10.memoetic_cli --project itau_15220012 --mode voice

# List recurring memes
python -m menir10.memoetic_cli --project itau_15220012 --mode memes
```

All modes accept optional parameters:
- `--log-file`: Path to the JSONL log file (default: `logs/menir10_interactions.jsonl`)

## Log Format

The memoetic layer expects JSONL files with this schema (minimal, tolerant):

```json
{
  "ts": "ISO8601 timestamp",
  "project_id": "identifier_string",
  "intent_profile": "note|call|summary|boot|...",
  "content": "main text of the interaction",
  "metadata": {
    "content": "optional override for content",
    "other_fields": "..."
  }
}
```

- `ts`: ISO 8601 formatted timestamp
- `project_id`: Project identifier (used to filter interactions)
- `intent_profile`: Type of interaction (informational; not currently used in analysis)
- `content`: Primary text to be analyzed. If empty, falls back to `metadata.content`
- `metadata`: Optional object that can override the `content` field

## Design Principles

1. **Deterministic**: No randomness, no LLM calls. Identical inputs always produce identical outputs.
2. **Fast**: Designed to run on logs of up to several hundred interactions with minimal latency.
3. **Tolerant**: Handles missing fields, blank lines, and mixed-language content gracefully.
4. **Language-Agnostic**: Uses a small, mixed Portuguese-English stopword list but respects Unicode and accented characters.
5. **Interpretable**: Every statistic (term frequency, variety ratio, quote length) is computed transparently and can be verified manually.

## Stopwords

The module uses a minimal, language-agnostic stopword set covering common Portuguese and English function words:

```
a, o, as, os, um, uma, de, do, da, das, dos,
e, ou, em, no, na, nas, nos, por, pra, para,
the, and, or, of, to, in, on, at, is, are,
eu, voce, você, que, se, com, sem, mas, não
```

This is intentionally small to preserve domain-specific vocabulary.

## Testing

Run the test suite for the memoetic module:

```bash
pytest tests/test_memoetic.py -v
```

Tests cover:
- **Profile extraction**: Verifies correct parsing and term frequency counting
- **Voice summarization**: Checks human-readable text generation and edge cases
- **Empty projects**: Handles projects with no interactions gracefully
- **Meme listing**: Validates structured output format and filtering by frequency

## Integration with Menir

The memoetic layer integrates with Menir's interaction logging:

1. **Logging**: Every user interaction (note, call, summary) is logged to `logs/menir10_interactions.jsonl`.
2. **On-Demand Analysis**: Use `extract_memoetics()` or `summarize_voice()` to analyze project history at any time.
3. **Narrative Insights**: The output can inform UX, project dashboard displays, or narrative-driven features.

Example: Display a project's "voice" on its dashboard:
```python
from menir10.memoetic import summarize_voice

voice_description = summarize_voice(project_id=user_project)
dashboard_widget = f"Project Narrative: {voice_description}"
```

## Limitations and Future Work

1. **Single Language**: Currently treats all text as a single language. Multi-language support could improve stopword filtering.
2. **No Semantic Clustering**: Identifies terms but not semantic concepts. Future work could use embeddings.
3. **No Temporal Patterns**: Does not track how themes evolve over time. Timeline-based analysis is a candidate for v2.
4. **Static Stopwords**: Stopword list is hardcoded. Could be externalized or learned from a corpus.

## References

- **JSONL Format**: [JSONL.org](http://jsonl.org)
- **Menir Architecture**: See `README.md` and `docs/MODEL.md`
- **Implementation**: `menir10/memoetic.py`
- **Tests**: `tests/test_memoetic.py`
- **Quick Start**: See `QUICKSTART.md` for usage examples
