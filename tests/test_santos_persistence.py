import pytest
import asyncio
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime
from src.v3.core.persistence import NodePersistenceOrchestrator
from src.v3.core.schemas.santos import SignalInput, InsightInput, DecisionHubEntry
from src.v3.core.schemas.identity import TenantContext

@pytest.fixture
def orchestrator():
    return NodePersistenceOrchestrator()

@pytest.fixture
def mock_tx():
    tx = MagicMock()
    # Mock tx.run to return a record-like object if needed
    tx.run.return_value.single.return_value = {"uid": "doc123"}
    return tx

@pytest.mark.asyncio
async def test_persist_signal(orchestrator, mock_tx):
    TenantContext.set("SANTOS")
    
    signal = SignalInput(
        uid="sig123",
        project="SANTOS",
        signal_type="TAX_ALERT",
        weight=Decimal("0.85"),
        origin_tenant_hash="abcde"
    )
    
    uid = await orchestrator.persist(signal, mock_tx)
    assert uid == "sig123"
    
    # Check if tx.run was called with correct properties in _merge_node
    # We look for the call that has 'signal_type' in its arguments
    merge_call = next(c for c in mock_tx.run.call_args_list if "signal_type" in c.kwargs)
    assert merge_call.kwargs["signal_type"] == "TAX_ALERT"
    assert merge_call.kwargs["weight"] == 0.85
    assert merge_call.kwargs["decay_lambda"] == 0.1
    assert "created_at" in merge_call.kwargs

@pytest.mark.asyncio
async def test_persist_insight(orchestrator, mock_tx):
    TenantContext.set("SANTOS")
    
    insight = InsightInput(
        uid="ins123",
        project="SANTOS",
        content="Important personal insight",
        decay_lambda=Decimal("0.05"),
        tags=["brainstorm"]
    )
    
    uid = await orchestrator.persist(insight, mock_tx)
    assert uid == "ins123"
    
    merge_call = next(c for c in mock_tx.run.call_args_list if "content" in c.kwargs)
    assert merge_call.kwargs["content"] == "Important personal insight"
    assert merge_call.kwargs["decay_lambda"] == 0.05
    assert merge_call.kwargs["tags"] == ["brainstorm"]

@pytest.mark.asyncio
async def test_persist_decision_hub(orchestrator, mock_tx):
    TenantContext.set("SANTOS")
    
    hub = DecisionHubEntry(
        uid="hub123",
        project="SANTOS"
    )
    
    uid = await orchestrator.persist(hub, mock_tx)
    assert uid == "hub123"
    
    merge_call = next(c for c in mock_tx.run.call_args_list if "DecisionHub" in c.args[0])
    assert merge_call.kwargs["uid"] == "hub123"
