import json
from datetime import date

import pytest

import menir10_export as m10


@pytest.fixture
def sample_entries():
    # Log sintético mínimo cobrindo os 3 projetos principais
    return [
        {
            "interaction_id": "u1",
            "ts": "2025-11-17T10:00:00Z",
            "project_id": "Tivoli",
            "role": "user",
            "content": "Primeiro contato Tivoli",
        },
        {
            "interaction_id": "a1",
            "ts": "2025-11-17T10:00:05Z",
            "project_id": "Tivoli",
            "role": "assistant",
            "content": "Resposta inicial Tivoli",
        },
        {
            "interaction_id": "u2",
            "ts": "2025-11-17T10:15:00Z",
            "project_id": "Tivoli",
            "role": "user",
            "content": "Detalhes extra Tivoli",
        },
        {
            "interaction_id": "u3",
            "ts": "2025-11-17T11:00:00Z",
            "project_id": "Itau_15220012",
            "role": "user",
            "content": "Pergunta Itaú",
        },
        {
            "interaction_id": "a3",
            "ts": "2025-11-17T11:00:05Z",
            "project_id": "Itau_15220012",
            "role": "assistant",
            "content": "Resposta Itaú",
        },
        {
            "interaction_id": "u4",
            "ts": "2025-11-18T09:00:00Z",
            "project_id": "Ibere",
            "role": "user",
            "content": "Contexto Iberê",
        },
    ]


def test_group_by_project_counts(sample_entries):
    grouped = m10.group_by_project(sample_entries)
    assert set(grouped.keys()) == {"Tivoli", "Itau_15220012", "Ibere"}
    assert len(grouped["Tivoli"]) == 3
    assert len(grouped["Itau_15220012"]) == 2
    assert len(grouped["Ibere"]) == 1


def test_top_projects_sorted(sample_entries):
    top = m10.top_projects(sample_entries, limit=2)
    assert len(top) == 2
    # Tivoli tem 3 interações, Itau_15220012 tem 2
    assert top[0][0] == "Tivoli"
    assert top[0][1] == 3
    assert top[1][0] == "Itau_15220012"
    assert top[1][1] == 2


def test_generate_cypher_contains_expected_nodes_and_edges(sample_entries):
    cypher = m10.generate_cypher(sample_entries)
    # Project nodes
    assert "Project" in cypher
    assert "Tivoli" in cypher
    assert "Itau_15220012" in cypher
    # Relationship label
    assert "HAS_INTERACTION" in cypher
    # Um dos IDs de interação deve aparecer
    assert "u1" in cypher


def test_generate_daily_report_md_filters_by_date(sample_entries):
    report = m10.generate_daily_report_md(
        sample_entries,
        target_date=date(2025, 11, 17),
        top_n=3,
        per_project_limit=2,
    )
    # Header + overview
    assert "Menir10 Daily Report" in report
    assert "- Total interactions: 5" in report  # só entradas de 17/11
    # Projetos do dia 17/11 precisam aparecer
    assert "## Tivoli" in report
    assert "## Itau_15220012" in report
    # Projeto só de 18/11 não deve aparecer nesse relatório filtrado
    assert "Ibere" not in report


def test_load_entries_from_jsonl_roundtrip(tmp_path, sample_entries):
    path = tmp_path / "menir10_sample.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for entry in sample_entries:
            f.write(json.dumps(entry) + "\n")

    loaded = m10.load_entries_from_jsonl(path)
    assert loaded == sample_entries
