from pathlib import Path
import json

from menir10.menir10_log import append_log


def test_append_log_writes_valid_jsonl(tmp_path):
    log_path = tmp_path / "test_menir10_interactions.jsonl"

    record = append_log(
        project_id="test_project",
        intent_profile="note",
        content="Teste unitário",
        log_path=log_path,
    )

    # arquivo existe
    assert log_path.exists()

    # uma linha gravada e JSON válido
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    loaded = json.loads(lines[0])

    # campos básicos
    assert loaded["project_id"] == "test_project"
    assert loaded["intent_profile"] == "note"
    assert loaded["metadata"]["content"] == "Teste unitário"

    # payload retornado bate com o gravado
    assert record["interaction_id"] == loaded["interaction_id"]
