
"""
Menir Astro Extension
"""
try:
    from .schema import BirthChart, Placement
    from .engine import MenirAstro
    from .time_engine import MenirTime
    ASTRO_AVAILABLE = True
except ImportError as e:
    print(f"DEBUG: Astra Extension Load Error: {e}")
    MenirAstro = None
    MenirTime = None
    BirthChart = None
    Placement = None
    ASTRO_AVAILABLE = False
