import json
from pathlib import Path

from menir10.memoetic import (
    extract_memoetics,
    summarize_voice,
    list_memes,
    MemoeticProfile,
)


def _write_log(tmp_path: Path, project_id: str = "itau_15220012") -> Path:
    log_path = tmp_path / "menir10_interactions.jsonl"
    entries = [
        {
            "ts": "2025-01-01T10:00:00-03:00",
            "project_id": project_id,
            "intent_profile": "note",
            "content": "Reunião com Itaú, discutir proposta de crédito com garantia.",
        },
        {
            "ts": "2025-01-02T11:00:00-03:00",
            "project_id": project_id,
            "intent_profile": "note",
            "content": "Escrever dossiê técnico do Itaú, revisar cláusulas abusivas.",
        },
        {
            "ts": "2025-01-03T12:00:00-03:00",
            "project_id": project_id,
            "intent_profile": "summary",
            "metadata": {
                "content": "Resumo do caso Itaú: foco em segurança jurídica e memória probatória."
            },
        },
    ]
    with log_path.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return log_path


def test_extract_memoetics_builds_profile(tmp_path):
    log_path = _write_log(tmp_path)
    profile = extract_memoetics("itau_15220012", log_path=log_path)

    assert isinstance(profile, MemoeticProfile)
    assert profile.project_id == "itau_15220012"
    assert profile.total_interactions == 3
    assert len(profile.top_terms) > 0
    assert any("ita" in term or "itau" in term for term, _ in profile.top_terms)


def test_summarize_voice_has_human_readable_text(tmp_path):
    log_path = _write_log(tmp_path)
    text = summarize_voice("itau_15220012", log_path=log_path)

    assert "Project 'itau_15220012'" in text
    assert "vocabulary" in text or "language" in text


def test_summarize_voice_handles_empty_project(tmp_path):
    log_path = tmp_path / "empty.jsonl"
    log_path.write_text("", encoding="utf-8")

    text = summarize_voice("unknown_project", log_path=log_path)
    assert "has no memoetic footprint" in text


def test_list_memes_structure(tmp_path):
    log_path = _write_log(tmp_path)
    data = list_memes("itau_15220012", log_path=log_path, min_freq=1)

    assert data["project_id"] == "itau_15220012"
    assert data["total_interactions"] == 3
    assert isinstance(data["terms"], list)
    assert isinstance(data["sample_quotes"], list)
