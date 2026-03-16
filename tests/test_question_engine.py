import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.v3.skills.question_engine import generate_question
from src.v3.core.schemas.identity import TenantContext

@pytest.fixture
def mock_intel():
    with patch("src.v3.skills.question_engine.MenirIntel") as mock:
        instance = mock.return_value
        instance.structured_inference = AsyncMock()
        yield instance

@pytest.fixture
def mock_bridge():
    with patch("src.v3.skills.question_engine.MenirBridge") as mock:
        bridge = mock.return_value
        bridge.driver.session = MagicMock()
        yield bridge

@pytest.mark.asyncio
async def test_entity_gap_triggers_question(mock_intel, mock_bridge):
    TenantContext.set("SANTOS")
    # 1. Mock Entity Extraction
    mock_intel.structured_inference.side_effect = [
        ["Ana Caroline"], # Entities extraction call
        "Qual o cargo atual da Ana Caroline na empresa?" # Question formulation call
    ]
    
    # 2. Mock Neo4j Gap Analysis
    mock_record = MagicMock()
    mock_record.__getitem__.side_effect = lambda key: {
        "n": {"name": "Ana Caroline", "role_or_context": "", "uid": "ana123"},
        "label": "Person"
    }[key]
    
    mock_tx = MagicMock()
    # Call order: 1. _find_gaps (entities not empty), 2. _get_urgent_signals
    mock_tx.run.side_effect = [
        [mock_record], # _find_gaps
        [] # _get_urgent_signals
    ]
    mock_bridge.driver.session.return_value.__enter__.return_value = mock_tx

    question = await generate_question("Encontrei a Ana Caroline hoje.", "user123")
    
    assert question == "Qual o cargo atual da Ana Caroline na empresa?"
    assert mock_intel.structured_inference.call_count == 2
    TenantContext.set(None)

@pytest.mark.asyncio
async def test_no_entity_no_signals_returns_none(mock_intel, mock_bridge):
    TenantContext.set("SANTOS")
    # 1. Mock Entity Extraction (None found)
    mock_intel.structured_inference.return_value = []
    
    # 2. Mock Neo4j
    mock_tx = MagicMock()
    # Call order: 1. _has_urgent_signals (entities is empty)
    mock_tx.run.return_value.single.return_value = {"has_urgent": False}
    mock_bridge.driver.session.return_value.__enter__.return_value = mock_tx

    question = await generate_question("Comprei um pão.", "user123")
    
    assert question is None
    TenantContext.set(None)

@pytest.mark.asyncio
async def test_decision_hub_signal_triggers_question(mock_intel, mock_bridge):
    TenantContext.set("SANTOS")
    # 1. Mock Entity Extraction (None)
    mock_intel.structured_inference.side_effect = [
        [], # No entities extraction call
        "Como a nova regra fiscal suíça afeta seus planos?" # Question formulation call
    ]
    
    # 2. Mock Neo4j (Urgent Signal)
    mock_tx = MagicMock()
    # Call order: 
    # 1. _has_urgent_signals (called because entities is empty)
    # (_find_gaps is called but returns [] immediately without tx.run)
    # 2. _get_urgent_signals
    mock_tx.run.side_effect = [
        MagicMock(single=lambda: {"has_urgent": True}), # _has_urgent_signals result
        [{"type": "SWISS_FISCAL_DRIFT", "desc": "Nova regra fiscal", "priority": 0.9}] # _get_urgent_signals result
    ]
    mock_bridge.driver.session.return_value.__enter__.return_value = mock_tx

    question = await generate_question("Vou viajar amanhã.", "user123")
    
    assert question == "Como a nova regra fiscal suíça afeta seus planos?"
    TenantContext.set(None)

@pytest.mark.asyncio
async def test_missing_context_raises_runtime_error(mock_intel, mock_bridge):
    TenantContext.set(None)
    with pytest.raises(RuntimeError) as excinfo:
        await generate_question("Oi", "user123")
    assert "question_engine chamado fora de contexto galvânico" in str(excinfo.value)
