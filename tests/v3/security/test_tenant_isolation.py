import pytest

from src.v3.core.schemas.identity import SecurityContextError, TenantContext, locked_tenant_context
from src.v3.core.synapse import MenirSynapse


def test_d_context_manager_circuit_breaker():
    """
    Test Case 1: Ensure that any attempt to switch TenantID within a locked context
    context manager raises a Hard Constraint Violation.
    """
    with locked_tenant_context("SANTOS"):
        assert TenantContext.get() == "SANTOS"

        # Simulating an internal function attempting to bypass isolation
        with pytest.raises(SecurityContextError, match="ISOLATION BREACH DETECTED"):
            with locked_tenant_context("BECO"):
                pass  # This should never execute


@pytest.mark.asyncio
async def test_d_synapse_middleware_failure():
    """
    Test Case 2: Validation of synapse.py failure.
    Test must FAIL (Red Phase) because 'synapse.py' does not yet support ContextVars.
    """

    class MockRunner:
        pass

    synapse = MenirSynapse(runner=MockRunner())
    captured_tenant = None
    original_queue = synapse._queue_command

    # We intercept the inner function to see if the Middleware properly injected the ContextVar
    async def intercept_queue(raw_input, origin):
        nonlocal captured_tenant
        captured_tenant = TenantContext.get()
        return await original_queue(raw_input, origin)

    synapse._queue_command = intercept_queue

    # Simulating the web request parser
    class MockRequest:
        def __init__(self, headers, json_data):
            self.headers = headers
            self._json = json_data

        async def json(self):
            return self._json

    # Send a payload explicitly scoped to SANTOS
    req = MockRequest(
        headers={"Authorization": "Bearer TOKEN_SANTOS_LIFE_JWT"},
        json_data={"intent": "Deploy code", "origin": "WEB_UI"},
    )

    await synapse.handle_command_http(req)

    # Asserting that synapse.py correctly set the Galvanic Isolation ContextVar.
    # THIS WILL FAIL because Phase 39 IoC is not yet implemented in synapse.py
    assert captured_tenant == "SANTOS", (
        "Galvanic Isolation Failed: Synapse did not lock the ContextVar for the execution loop!"
    )
