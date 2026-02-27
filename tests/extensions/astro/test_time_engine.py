
import pytest
from datetime import datetime
try:
    from src.v3.extensions.astro.time_engine import MenirTime
except ImportError:
    MenirTime = None

@pytest.mark.skipif(MenirTime is None, reason="Astro Extension not loaded")
def test_saturn_pisces_judge():
    """Verifies that Saturn is detected in Pisces in mid-2024."""
    timer = MenirTime()
    
    # Date: June 1st, 2024
    target_date = datetime(2024, 6, 1, 12, 0)
    
    # Dummy natal data (we just want to trigger the calculation logic to inspect the transit object internally, 
    # but the method returns aspects. So let's mock a natal planet that would receive an aspect from Saturn in Pisces.)
    # Saturn in 2024 is around 18 degrees Pisces (Pisces is 330-360 abs lon. 18 Pisces = 348 abs lon).
    # If we put a Natal Sun at 18 Virgo (168 abs lon), it should be an Opposition (180 deg diff).
    
    # Pisces 18 deg -> ~348 deg
    # Virgo 18 deg -> ~168 deg
    # Diff = 180 deg (Opposition)
    
    mock_natal = [
        {"body_name": "Sun", "longitude": 168.0} # 18 Virgo
    ]
    
    forecast = timer.calculate_transits(mock_natal, target_date)
    
    # Search for Saturn aspect
    saturn_aspect = None
    for a in forecast['aspects']:
        if a['transit_planet'] == 'Saturn':
            saturn_aspect = a
            break
            
    assert saturn_aspect is not None, "Saturn should be aspecting the Natal Sun."
    assert saturn_aspect['aspect'] == 'Opposition', f"Expected Opposition, got {saturn_aspect['aspect']}"
    assert saturn_aspect['transit_sign'] == 'Pisces', f"Saturn should be in Pisces, got {saturn_aspect['transit_sign']}"
    
    print(f"\n✅ Logic verified: Saturn was in {saturn_aspect['transit_sign']} on {target_date.date()}")

def test_filter_fast_planets():
    """Ensures Moon/Mercury (fast planets) are ignored."""
    timer = MenirTime()
    target_date = datetime.now()
    
    # Natal Sun at current Moon position (guaranteed aspect if not filtered)
    # But we can't easily predict Moon position without calc.
    # Instead, we rely on the output NOT containing 'Moon' as transit_planet.
    
    mock_natal = [{"body_name": "Sun", "longitude": 0}]
    forecast = timer.calculate_transits(mock_natal, target_date)
    
    for a in forecast['aspects']:
        assert a['transit_planet'] in ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Chiron", "North Node", "South Node"], \
            f"Fast planet {a['transit_planet']} leaked through filter!"

if __name__ == "__main__":
    test_saturn_pisces_judge()
    test_filter_fast_planets()
    print("All tests passed.")
