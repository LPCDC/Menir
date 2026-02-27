
import pytest
from unittest.mock import MagicMock, patch
from neo4j.exceptions import ServiceUnavailable, TransientError
from tenacity import RetryError
from src.v3.menir_bridge import MenirBridge
from src.v3.tenant_middleware import current_tenant_id


def test_bridge_retry_success(mock_neo4j_session):
    """
    Simulate a transient failure (ServiceUnavailable) that succeeds after retries.
    Targeting check_evidence method which has @retry.
    """
    with patch("src.v3.menir_bridge.GraphDatabase.driver") as mock_driver_cls:
        mock_driver = mock_driver_cls.return_value
        mock_session = mock_driver.session.return_value.__enter__.return_value
        
        # Setup Success Result
        success_result = MagicMock()
        success_result.single.return_value = {"exists": True}

        # Setup Side Effect: Fail twice (raise), then return Success Result (callable)
        # Note: side_effect can mix Exceptions and Return Values
        mock_session.run.side_effect = [
            ServiceUnavailable("Connection Lost"),
            ServiceUnavailable("Still Lost"),
            success_result
        ]

        bridge = MenirBridge()
        
        # Set tenant context so TenantAwareDriver allows the query
        token = current_tenant_id.set("test_tenant")
        try:
            result = bridge.check_evidence("hash", "proj")
        finally:
            current_tenant_id.reset(token)
        
        # Verify
        assert result is True
        assert mock_session.run.call_count == 3

def test_bridge_max_retries_exceeded(mock_neo4j_session):
    """
    Simulate a persistent failure that eventually raises RetryError.
    """
    with patch("src.v3.menir_bridge.GraphDatabase.driver") as mock_driver_cls:
        mock_driver = mock_driver_cls.return_value
        mock_session = mock_driver.session.return_value.__enter__.return_value
        
        # Always fail
        mock_session.run.side_effect = ServiceUnavailable("Dead DB")

        bridge = MenirBridge()

        # Set tenant context so TenantAwareDriver allows the query
        token = current_tenant_id.set("test_tenant")
        try:
            # It should eventually give up
            with pytest.raises((RetryError, ServiceUnavailable)):
                bridge.check_evidence("hash", "proj")
        finally:
            current_tenant_id.reset(token)
