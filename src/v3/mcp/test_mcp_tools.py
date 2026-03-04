import asyncio
from unittest.mock import MagicMock, patch

import pytest

from src.v3.mcp.protools import MenirTools
from src.v3.mcp.security import PiiFilter

# ==========================================
# Security Tests
# ==========================================


def test_pii_redaction():
    node = {
        "name": "Ricardo",
        "cpf": "123.456.789-00",
        "email_personal": "ricardo@gmail.com",
        "role": "Admin",
    }
    secure = PiiFilter.redact_node(node)

    assert secure["name"] == "Ricardo"
    assert secure["role"] == "Admin"
    assert secure["cpf"] == "[REDACTED_PII]"
    assert secure["email_personal"] == "[REDACTED_PII]"


def test_log_redaction():
    line = "User ricardo@test.com logged in with CPF 111.222.333-44"
    clean = PiiFilter.redact_log_line(line)

    assert "[EMAIL_REDACTED]" in clean
    assert "[CPF_REDACTED]" in clean
    assert "ricardo@test.com" not in clean


# ==========================================
# Tool Tests
# ==========================================


@pytest.mark.asyncio
async def test_get_strict_schema():
    schema = await MenirTools.get_strict_schema()
    assert "labels" in schema
    assert "Person" in schema["labels"]


@pytest.mark.asyncio
async def test_search_logs_mock():
    # Mock file reading
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        mock_file = MagicMock()
        # Create a line > 500 chars
        long_line = "A" * 600
        mock_file.readlines.return_value = ["Line 1", long_line]
        mock_open.return_value.__enter__.return_value = mock_file

        # Patch os.path.exists to True
        with patch("os.path.exists", return_value=True):
            logs = await MenirTools.search_logs(limit=10)

            assert len(logs) == 2
            assert logs[0] == "Line 1"
            assert len(logs[1]) < 550  # 500 + suffix
            assert "...[TRUNCATED]" in logs[1]


@pytest.mark.asyncio
async def test_explain_node_timeout():
    # Mock MenirBridge to simulate timeout (sleep > 5s) via side_effect??
    # Actually simpler: Tool catches asyncio.TimeoutError.
    # We can mock asyncio.wait_for to raise TimeoutError.

    with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError):
        # We also need to mock MenirBridge so __init__ doesn't fail on real connection if env missing
        with patch("src.v3.mcp.protools.MenirBridge") as MockBridge:  # noqa: F841
            result = await MenirTools.explain_node("any-uuid")
            assert "error" in result
            assert "timeout" in result["error"].lower()
            assert result["status"] == "offline"


if __name__ == "__main__":
    msg = "Run 'pytest src/v3/mcp/test_mcp_tools.py' to execute."
    print(msg)
