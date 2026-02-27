
"""
Menir Command Controller (H4)
The "Agent" logic that connects the CLI (User) to the Engine (Astro) and the Memory (Bridge).
Adheres to the GraphRAG Manifesto: Strict Ground Truth.
"""
import logging
from datetime import datetime
from src.v3.menir_bridge import MenirBridge
from src.v3.schema import Person

# Dynamic Extension Loading
try:
    from src.v3.extensions.astro import MenirAstro, BirthChart, Placement, ASTRO_AVAILABLE
except ImportError as e:
    print(f"DEBUG: Import Error: {e}")
    MenirAstro = None
    ASTRO_AVAILABLE = False

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MenirCMD")

class MenirCommander:
    def __init__(self):
        self.bridge = MenirBridge()
        self.astro = MenirAstro() if ASTRO_AVAILABLE else None

    def close(self):
        self.bridge.close()

    def create_chart(self, name: str, dt: datetime, city: str, lat: float, lon: float):
        """
        1. Calculate Chart (Engine).
        2. Create/Find Person.
        3. Save Chart & Placements (Bridge).
        4. Link Person -> Chart -> Placements -> Planets/Signs/Houses.
        """
        if not self.astro:
            logger.error("❌ Astro Extension not loaded. Cannot create chart.")
            return None

        logger.info(f"✨ Computing Chart for: {name} ({dt})")
        
        # 1. Calculate
        chart_node, placements = self.astro.calculate_chart(dt, lat, lon, city)
        
        # 2. Person
        # Use MenirVital to align with Genesis and Core Ontology
        person = Person(name=name, project="MenirVital", is_real=True)
        self.bridge.merge_node(person)
        
        # 3. Chart
        self.bridge.merge_node(chart_node)
        
        # Link Person -> Chart
        # Link to the MenirVital Person
        # Link Person -> Chart
        query_link_chart = """
        MATCH (p:Person {name: $p_name, project: $proj})
        MATCH (c:BirthChart {uid: $c_uid})
        MERGE (p)-[r:HAS_BIRTHCHART]->(c)
        RETURN count(r) as cnt
        """
        with self.bridge.driver.session() as session:
            res = session.run(query_link_chart, p_name=name, proj="MenirVital", c_uid=chart_node.uid).single()

            # Note: MERGE returns 1 created or 0 if existing. But we just want to ensure it exists.
            # Actually, let's just log verification.
            if not res:
                logger.error(f"❌ FAILED to Link Chart to Person '{name}' (Project: MenirVital). Match failed.")
            else:
                logger.info(f"✅ Link Created: Person -> Chart")
        logger.info(f"🌌 Linking {len(placements)} Placements...")
        for p in placements:
            self.bridge.merge_node(p)
            
            # Link Chart -> Placement
            query_c_p = """
            MATCH (c:BirthChart {uid: $c_uid})
            MATCH (p:Placement {uid: $p_uid})
            MERGE (c)-[:HAS_PLACEMENT]->(p)
            """
            with self.bridge.driver.session() as session:
                session.run(query_c_p, c_uid=chart_node.uid, p_uid=p.uid)
                
            # Link Placement -> CelestialBody
            # Note: We rely on name matching since Static Nodes have no UIDs in this context easily passed
            body_name = p.properties['body_name']
            query_p_body = """
            MATCH (p:Placement {uid: $p_uid})
            MATCH (b:CelestialBody {name: $b_name})
            MERGE (p)-[:OF_PLANET]->(b)
            """
            with self.bridge.driver.session() as session:
                session.run(query_p_body, p_uid=p.uid, b_name=body_name)
                
            # Link Placement -> ZodiacSign
            sign_name = p.properties['sign_name']
            query_p_sign = """
            MATCH (p:Placement {uid: $p_uid})
            MATCH (s:ZodiacSign {name: $s_name})
            MERGE (p)-[:IN_SIGN]->(s)
            """
            with self.bridge.driver.session() as session:
                session.run(query_p_sign, p_uid=p.uid, s_name=sign_name)
                
            # Todo: Houses Logic (Requires House Calculation in Engine first, currently -1)
            
        logger.info("✅ Chart Created & Linked.")
        return chart_node.uid

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Menir Astro Command Interface")
    parser.add_argument("--name", required=True, help="Person Name")
    parser.add_argument("--date", required=True, help="ISO Format Date (YYYY-MM-DDTHH:MM)")
    parser.add_argument("--city", required=True, help="City Name")
    parser.add_argument("--lat", type=float, default=-23.55, help="Latitude (Default: SP)")
    parser.add_argument("--lon", type=float, default=-46.63, help="Longitude (Default: SP)")
    
    args = parser.parse_args()
    
    cmd = MenirCommander()
    try:
        dt = datetime.fromisoformat(args.date)
        uid = cmd.create_chart(args.name, dt, args.city, args.lat, args.lon)
        print(f"OUTPUT_UID:{uid}")
    except Exception as e:
        logger.error(f"Command Failed: {e}")
        exit(1)
    finally:
        cmd.close()
