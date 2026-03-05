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
    MenirAstro = None  # type: ignore[assignment]
    MenirTime = None  # type: ignore[assignment]
    BirthChart = None  # type: ignore[assignment]
    Placement = None  # type: ignore[assignment]
    ASTRO_AVAILABLE = False
