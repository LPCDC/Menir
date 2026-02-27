
"""
Menir Time Engine (Horizon 5)
Stateless calculator for Astrological Transits and Aspects.
Computes "Now vs Natal" without database persistence.
"""
from datetime import datetime
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MenirTime")

class MenirTime:
    def __init__(self):
        # Major aspect angles and their standard orbs
        self.ASPECTS = {
            "Conjunction": {"angle": 0, "orb": 8},
            "Opposition": {"angle": 180, "orb": 8},
            "Square": {"angle": 90, "orb": 7},
            "Trine": {"angle": 120, "orb": 7},
            "Sextile": {"angle": 60, "orb": 5},
        }

    def _get_angle_diff(self, a, b):
        """Calculates the shortest distance between two points on a 360 circle."""
        diff = abs(a - b)
        return diff if diff <= 180 else 360 - diff

    def calculate_transits(self, natal_placements: list, target_dt: datetime, lat: float = 0, lon: float = 0) -> dict:
        """
        Calculates aspects between the Sky (at target_dt) and Natal Placements.
        
        natal_placements: List of dicts with {'body_name': str, 'longitude': float}
        """
        # 1. Calculate the Sky (Transits)
        # Using a default GeoPos if not provided (Transits are mostly global for planets)
        date = Datetime(target_dt.strftime("%Y/%m/%d"), target_dt.strftime("%H:%M"), "+00:00")
        pos = GeoPos(lat, lon)
        sky = Chart(date, pos, IDs=const.LIST_OBJECTS)
        
        forecast = {
            "target_date": target_dt.isoformat(),
            "aspects": []
        }
        
        
        # Major Planets for Strategic Forecasting (Jupiter to Pluto + Nodes)
        MAJOR_PLANETS = ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Chiron", "North Node", "South Node"]

        # 2. Compare Sky Planets vs Natal Planets
        for transit_body_id in MAJOR_PLANETS:
            if transit_body_id not in const.LIST_OBJECTS and transit_body_id not in ["Chiron", "North Node", "South Node"]:
                 # Handling case where flatlib might not have full list in LIST_OBJECTS or naming differs
                 # Actually flatlib uses 'Chiron', 'North Node' etc are specific.
                 # Let's check reliability. For now, trust input or fallback.
                 pass

            try:
                t_obj = sky.get(transit_body_id)
            except:
                continue
                
            t_lon = float(t_obj.lon)
            
            for n_p in natal_placements:
                n_body = n_p['body_name']
                n_lon = n_p['longitude']
                
                # Calculate actual distance
                dist = self._get_angle_diff(t_lon, n_lon)
                
                # Check for major aspects
                for name, data in self.ASPECTS.items():
                    target_angle = data['angle']
                    orb = data['orb']
                    
                    if abs(dist - target_angle) <= orb:
                        exactness = 1.0 - (abs(dist - target_angle) / orb)
                        forecast['aspects'].append({
                            "transit_planet": transit_body_id,
                            "aspect": name,
                            "natal_planet": n_body,
                            "orb_diff": round(abs(dist - target_angle), 2),
                            "exactness": round(exactness, 2),
                            "transit_sign": t_obj.sign
                        })
                        
        return forecast

if __name__ == "__main__":
    # Test Logic
    # Example: Daniella's Sun at ~280 degrees (Capricorn 10)
    mock_natal = [
        {"body_name": "Sun", "longitude": 280.5},
        {"body_name": "Moon", "longitude": 340.0}
    ]
    
    timer = MenirTime()
    now = datetime.now()
    res = timer.calculate_transits(mock_natal, now)
    
    print(f"--- Menir Forecast for {now.date()} ---")
    for a in res['aspects']:
        print(f"✨ {a['transit_planet']} ({a['transit_sign']}) {a['aspect']} Natal {a['natal_planet']} (Orb: {a['orb_diff']}°)")
