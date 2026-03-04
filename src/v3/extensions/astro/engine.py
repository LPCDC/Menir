"""
Menir Astro Engine
Wraps flatlib to calculate planetary positions and houses.
Returns Pydantic objects defined in schema_astro.py.
"""

from datetime import datetime

from flatlib import const
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

from .schema import BirthChart, Placement


class MenirAstro:
    def __init__(self):
        pass

    def calculate_chart(
        self, dt: datetime, lat: float, lon: float, city: str = "Unknown"
    ) -> tuple[BirthChart, list[Placement]]:
        """
        Calculates the Birth Chart.
        Returns: (BirthChart Node, List of Placement Nodes)
        """
        # 1. Convert to Flatlib Date
        date = Datetime(
            dt.strftime("%Y/%m/%d"), dt.strftime("%H:%M"), "+00:00"
        )  # Assuming UTC for simplicity or handle offsets
        pos = GeoPos(lat, lon)

        # 2. Calculate Chart
        chart = Chart(date, pos, IDs=const.LIST_OBJECTS)

        # 3. Create Chart Node
        chart_node = BirthChart(
            name=f"Chart: {dt.isoformat()}",
            timestamp=dt.isoformat(),
            latitude=lat,
            longitude=lon,
            city=city,
            project="MenirAstro",  # Required by BaseNode
        )

        # 4. Create Placements
        placements = []
        for body_id in const.LIST_OBJECTS:
            obj = chart.get(body_id)

            p = Placement(
                name=f"{body_id} Placement",
                longitude=float(obj.lon),
                degree_in_sign=float(obj.lon % 30),
                is_retrograde=False,
                project="MenirAstro",  # Required by BaseNode
            )

            # Add dynamic properties
            p.properties["body_name"] = body_id
            p.properties["sign_name"] = obj.sign
            p.properties["house_number"] = -1

            placements.append(p)

        return chart_node, placements


if __name__ == "__main__":
    # Internal Test
    now = datetime.now()
    astro = MenirAstro()
    chart, planets = astro.calculate_chart(now, -23.55, -46.63, "Sao Paulo")
    print(f"Chart: {chart.name}")
    for p in planets:
        print(
            f"{p.properties['body_name']} in {p.properties['sign_name']} ({p.degree_in_sign:.2f})"
        )
