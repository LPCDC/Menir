"""
Menir Astro Extension
"""

try:
    from .engine import MenirAstro
    from .schema import BirthChart, Placement
    from .time_engine import MenirTime

    ASTRO_AVAILABLE = True
except ImportError as e:
    print(f"DEBUG: Astra Extension Load Error: {e}")
    from typing import Any
    MenirAstro: Any = None  # type: ignore[no-redef]
    MenirTime: Any = None  # type: ignore[no-redef]
    BirthChart: Any = None  # type: ignore[no-redef]
    Placement: Any = None  # type: ignore[no-redef]
    ASTRO_AVAILABLE = False
