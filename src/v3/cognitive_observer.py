"""
Menir Cognitive Observer
Horizon 3 - Innovation Frontier

Enforces strict observability tracking (RAGAS/TruLens style metrics)
and implements Human-in-the-Loop (HITL) manual gating for high-risk executions.
"""

import logging
import uuid
import time
from typing import Dict, Any, Callable
from src.v3.menir_bridge import MenirBridge

logger = logging.getLogger("CognitiveObserver")
logger.setLevel(logging.INFO)

class HighRiskExecutionBlocked(Exception):
    """Raised when an automated agent attempts to commit a high-risk finding without human consent."""
    pass

class CognitiveObserver:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.bridge = MenirBridge()

    def track_llm_execution(self, prompt: str, llm_func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Wraps an LLM function call to capture performance metrics and token estimates.
        """
        logger.info(f"👁️ [Observer] Tracking execution. Estimated Prompt Tokens: {len(prompt) // 4}")
        start_t = time.perf_counter()
        
        try:
            # Execute Model
            result = llm_func(prompt, *args, **kwargs)
            duration = time.perf_counter() - start_t
            
            # Estimate completion size
            completion_tokens = len(str(result)) // 4
            logger.info(f"✅ [Observer] Execution complete. Duration: {duration:.2f}s | Output Tokens: {completion_tokens}")
            
            # Persist Audit Log
            self._log_execution(prompt, result, duration, completion_tokens)
            return result
            
        except Exception as e:
            duration = time.perf_counter() - start_t
            logger.error(f"❌ [Observer] Execution FAILED after {duration:.2f}s: {e}")
            raise

    def enforce_hitl(self, task_name: str, payload_summary: str, bypass_for_test=False):
        """
        Human-In-The-Loop Checkpoint.
        Halts the execution pipeline until a human explicitly grants permission.
        """
        logger.critical(f"⚠️ [HITL CHECKPOINT] Requesting clearance for: {task_name}")
        logger.warning(f"📄 Task Payload: {payload_summary}")
        
        if bypass_for_test:
            logger.info("🔓 [HITL] Bypass flag active. Simulating human APPROVAL.")
            return True
        
        # In a real environment, this might block waiting on a webhook,
        # Slack message, or UI button press. Here we simulate a hard block unless bypassed.
        try:
            consent = input("Grant execution permission? (Y/N): ")
            if consent.strip().upper() == "Y":
                logger.info("🔓 [HITL] Human granted execution permission.")
                return True
            else:
                logger.error("🔒 [HITL] Human denied permission.")
                raise HighRiskExecutionBlocked("Human operator aborted the high-risk task.")
        except EOFError:
             logger.error("🔒 [HITL] No interactive TTY available. Failing closed.")
             raise HighRiskExecutionBlocked("Task requires direct human input to proceed.")

    def _log_execution(self, prompt: str, result: str, duration: float, out_tokens: int):
        query = """
        MERGE (a:LLMAuditLog {id: $id})
        SET a.tenant_id = $tenant,
            a.duration_sc = $duration,
            a.out_tokens = $tokens,
            a.timestamp = datetime()
        """
        try:
            with self.bridge.driver.session() as session:
                 session.run(query, 
                             id=str(uuid.uuid4()), 
                             tenant=self.tenant_id, 
                             duration=duration, 
                             tokens=out_tokens)
        except Exception as e:
             logger.warning(f"Failed to write audit log to DB: {e}")

# Example mock agent
def mock_llm_agent(prompt: str):
    time.sleep(0.5) # simulate latency
    return "This is a simulated forensic finding stating massive fraud."

if __name__ == "__main__":
    observer = CognitiveObserver("PROJECT_CORE")
    
    # 1. Track Metrics
    result = observer.track_llm_execution("Analyze these records for fraud...", mock_llm_agent)
    
    # 2. HITL Barrier
    try:
        observer.enforce_hitl("Commit Forensic Fraud Audit", result, bypass_for_test=True)
        print("Pipeline permitted to finalize operation.")
    except HighRiskExecutionBlocked:
        print("Pipeline aborted securely.")
