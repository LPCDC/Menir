"""PerceptionState: minimal state container for interactions."""

from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, Any, Optional


class PerceptionState:
    """Container for interaction state with timestamps and metadata."""

    def __init__(
        self,
        project_id: str,
        intent_profile: str,
        interaction_id: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        flags: Optional[Dict[str, bool]] = None,
    ):
        """Initialize PerceptionState.
        
        Args:
            project_id: Identifier for the project
            intent_profile: Intent profile name
            interaction_id: UUID for interaction (generated if not provided)
            created_at: ISO8601 creation timestamp (set on start_interaction if not provided)
            updated_at: ISO8601 update timestamp (set on start_interaction if not provided)
            flags: Dictionary of boolean flags
        """
        self.interaction_id = interaction_id or str(uuid4())
        self.project_id = project_id
        self.intent_profile = intent_profile
        self.created_at = created_at
        self.updated_at = updated_at
        self.flags = flags or {}

    @staticmethod
    def _now() -> str:
        """Return current UTC time as ISO8601 string."""
        return datetime.now(timezone.utc).isoformat()

    def start_interaction(self) -> None:
        """Initialize interaction timestamps."""
        now = self._now()
        self.created_at = now
        self.updated_at = now

    def touch(self) -> None:
        """Update the interaction's updated_at timestamp."""
        self.updated_at = self._now()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to plain dictionary (no datetime/UUID objects)."""
        return {
            "interaction_id": self.interaction_id,
            "project_id": self.project_id,
            "intent_profile": self.intent_profile,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "flags": self.flags,
        }
