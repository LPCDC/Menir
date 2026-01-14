import json
from unittest.mock import MagicMock, patch
import pytest

# We mock OpenAI before importing agent because usually it requires the lib
with patch.dict("sys.modules", {"openai": MagicMock()}):
    from menir_core.rag.agent import NarrativeAgent

@patch("menir_core.rag.agent.OpenAI")
@patch("menir_core.rag.agent.os.getenv")
def test_agent_initialization(mock_getenv, mock_openai):
    mock_getenv.return_value = "fake-key"
    agent = NarrativeAgent()
    assert agent.client is not None
    assert agent.model == "gpt-4o"

@patch("menir_core.rag.agent.OpenAI")
@patch("menir_core.rag.agent.os.getenv")
@patch("menir_core.rag.agent.query_narrative_graph")
def test_agent_tool_call_loop(mock_tool, mock_getenv, mock_openai):
    mock_getenv.return_value = "fake-key"
    
    # Setup mocks
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    # First response: Call Tool
    msg_tool_call = MagicMock()
    msg_tool_call.tool_calls = [MagicMock()]
    msg_tool_call.tool_calls[0].function.name = "query_narrative_graph"
    msg_tool_call.tool_calls[0].function.arguments = '{"query": "MATCH (n) RETURN n"}'
    msg_tool_call.content = None
    
    # Second response: Final Answer
    msg_final = MagicMock()
    msg_final.tool_calls = None
    msg_final.content = "Here is the answer."
    
    # Mock completions.create to return first response then second
    mock_client.chat.completions.create.side_effect = [
        MagicMock(choices=[MagicMock(message=msg_tool_call)]),
        MagicMock(choices=[MagicMock(message=msg_final)])
    ]
    
    # Mock tool output
    mock_tool.return_value = '[{"name": "Neo"}]'
    
    agent = NarrativeAgent()
    response = agent.chat("Who is Neo?")
    
    assert response == "Here is the answer."
    assert mock_tool.called
    assert len(agent.conversation_history) >= 3 # System + User + ToolCall + ToolResult + Final
