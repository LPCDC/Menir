
import pytest
from datetime import datetime
from src.v3.menir_astro import MenirAstro, BirthChart

# Pytest fixture if we needed complex setup, but this is pure math
def test_calculate_chart_structure():
    """Verifies that the chart calculation returns correct data structures."""
    astro = MenirAstro()
    dt = datetime(2023, 1, 1, 12, 0, 0) # UTC
    
    chart, placements = astro.calculate_chart(dt, 0.0, 0.0, "Null Island")
    
    assert isinstance(chart, BirthChart)
    assert chart.city == "Null Island"
    assert len(placements) > 0  # Should have Sun, Moon, etc.

def test_mars_position_known_date():
    """
    Verifies Mars position on a specific date.
    Date: 2023-01-01 12:00 UTC
    Mars was in Gemini (Retrograde).
    """
    astro = MenirAstro()
    dt = datetime(2023, 1, 1, 12, 0, 0)
    
    chart, placements = astro.calculate_chart(dt, 0.0, 0.0, "Greenwich")
    
    mars = next((p for p in placements if p.properties['body_name'] == 'Mars'), None)
    assert mars is not None
    assert mars.properties['sign_name'] == 'Gemini'
    # Precision check not needed for V1, just getting the Sign right is huge.
