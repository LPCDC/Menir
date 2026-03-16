import pytest
from decimal import Decimal
from pydantic import ValidationError
from src.v3.core.schemas.santos import SignalInput, InsightInput, DecisionHubEntry

def test_signal_input_valid():
    signal = SignalInput(
        signal_type="TAX_ALERT",
        weight=Decimal("0.85"),
        description="Test signal",
        origin_tenant_hash="abc123hash"
    )
    assert signal.signal_type == "TAX_ALERT"
    assert signal.weight == Decimal("0.85")
    assert signal.origin_tenant_hash == "abc123hash"

def test_signal_input_bounds():
    # Valid bounds
    SignalInput(signal_type="A", weight=Decimal("0"), origin_tenant_hash="H")
    SignalInput(signal_type="A", weight=Decimal("1"), origin_tenant_hash="H")
    
    # Invalid bounds
    with pytest.raises(ValidationError):
        SignalInput(signal_type="A", weight=Decimal("1.01"), origin_tenant_hash="H")
    with pytest.raises(ValidationError):
        SignalInput(signal_type="A", weight=Decimal("-0.01"), origin_tenant_hash="H")

def test_signal_input_extra_forbid():
    with pytest.raises(ValidationError):
        SignalInput(
            signal_type="A", 
            weight=Decimal("0.5"), 
            origin_tenant_hash="H",
            something_else="forbidden"
        )

def test_insight_input_valid():
    insight = InsightInput(content="New strategy")
    assert insight.content == "New strategy"
    assert insight.decay_lambda == Decimal("0.05") # default
    assert insight.tags is None

def test_insight_input_custom():
    insight = InsightInput(content="Old info", decay_lambda=Decimal("0.5"), tags=["urgent"])
    assert insight.decay_lambda == Decimal("0.5")
    assert insight.tags == ["urgent"]

def test_insight_input_extra_forbid():
    with pytest.raises(ValidationError):
        InsightInput(content="A", extra_stuff="forbidden")

def test_decision_hub_entry_no_fields():
    # Should work with no arguments
    DecisionHubEntry()
    
    # Should fail with any argument due to extra="forbid"
    with pytest.raises(ValidationError):
        DecisionHubEntry(uid="manual_uid")
