from typing import Any, Literal

from pydantic import Field

from src.v3.core.schemas.base import BaseNode


class CelestialBody(BaseNode):
    """
    Represents a Planet or Luminary (e.g., Sun, Moon, Mars).
    Static Node.
    """

    name: str = Field(..., description="English Name (e.g., Mars)")
    archetype: str = Field(..., description="Jungian/Universal Archetype")

    def __init__(self, **data):
        super().__init__(**data)
        self.labels.extend(["CelestialBody", "Planet"])


class ZodiacSign(BaseNode):
    """
    Represents a 30-degree sector of the Zodiac.
    Static Node.
    """

    name: str = Field(..., description="English Name (e.g., Aries)")
    element: Literal["Fire", "Earth", "Air", "Water"]
    modality: Literal["Cardinal", "Fixed", "Mutable"]
    ruler: str = Field(..., description="Traditional Ruling Planet")

    def __init__(self, **data):
        super().__init__(**data)
        self.labels.extend(["ZodiacSign", "Sign"])


class House(BaseNode):
    """
    Represents an astrological House (1-12).
    Static Node.
    """

    number: int = Field(..., ge=1, le=12)
    domain: str = Field(..., description="Area of Life (e.g., Career, Home)")
    name: str = Field(..., description="House Label")

    def __init__(self, **data):
        super().__init__(**data)
        self.labels.extend(["House"])
        self.name = f"House {self.number}"


class BirthChart(BaseNode):
    """
    Represents a Snapshot of the Sky at a specific moment.
    Dynamic Node (One per Person/Event).
    """

    timestamp: str = Field(..., description="ISO 8601 Datetime of Event")
    latitude: float
    longitude: float
    city: str
    name: str = Field(..., description="Descriptive Name")
    properties: dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data):
        super().__init__(**data)
        self.labels.extend(["BirthChart", "Chart"])
        self.name = f"Chart: {self.timestamp} ({self.city})"


class Placement(BaseNode):
    """
    Represents a specific position (e.g., Mars in Aries in House 5).
    Dynamic Node.
    """

    longitude: float = Field(..., description="0-360 degrees absolute longitude")
    degree_in_sign: float = Field(..., description="0-29.99 degrees relative to sign")
    is_retrograde: bool = False
    name: str = Field(..., description="Descriptive Name")
    properties: dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data):
        super().__init__(**data)
        self.labels.extend(["Placement"])
