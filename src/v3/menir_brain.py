
"""
Menir Brain (Phase 4: Agentic Loop)
The "Corpus Callosum" unifying Graph (Astro) and Vector (Context) data.
"""
import logging
import os
from typing import Optional, List
from src.v3.menir_bridge import MenirBridge
from src.v3.menir_intel import MenirIntel
try:
    from src.v3.extensions.astro import MenirTime
    ASTRO_AVAILABLE = True
except ImportError:
    MenirTime = None
    ASTRO_AVAILABLE = False

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MenirBrain")

class MenirBrain:
    def __init__(self):
        self.bridge = MenirBridge()
        self.intel = MenirIntel(api_key=os.getenv("GOOGLE_API_KEY"))
        self.timer = MenirTime() if ASTRO_AVAILABLE else None

    def close(self):
        self.bridge.close()

    def get_astro_context(self, person_name: str) -> str:
        """Fetches the astrological placements of a person from the graph."""
        query = """
        MATCH (p:Person {name: $name})-[r:HAS_BIRTHCHART]->(c:BirthChart)-[:HAS_PLACEMENT]->(pl:Placement)
        MATCH (pl)-[:OF_PLANET]->(body:CelestialBody)
        MATCH (pl)-[:IN_SIGN]->(sign:ZodiacSign)
        RETURN body.name as planet, sign.name as sign, pl.house as house
        ORDER BY house ASC
        """
        with self.bridge.driver.session() as session:
            results = session.run(query, name=person_name).data()
            if not results:
                return f"No astrological chart found for {person_name}."
            
            context = f"Astrological Chart for {person_name}:\n"
            for r in results:
                context += f"- {r['planet']} in {r['sign']} (House {r['house']})\n"
            return context

    def get_forecast_context(self, person_name: str, target_date_str: str = None) -> str:
        """Calculates transits for a person and returns an aspect context string."""
        if not self.timer:
            return "Forecast unavailable: Astro Extension not loaded."
            
        target_dt = datetime.fromisoformat(target_date_str) if target_date_str else datetime.now()
        
        # 1. Fetch Natal Data for aspects
        query = """
        MATCH (p:Person {name: $name})-[:HAS_BIRTHCHART]->(c:BirthChart)-[:HAS_PLACEMENT]->(pl:Placement)
        MATCH (pl)-[:OF_PLANET]->(body:CelestialBody)
        RETURN body.name as body_name, pl.longitude as longitude
        """
        with self.bridge.driver.session() as session:
            natal_data = session.run(query, name=person_name).data()
            if not natal_data:
                return f"Cannot calculate forecast: No Natal data for {person_name}."
            
            # 2. Calculate Transits (Stateless)
            forecast_data = self.timer.calculate_transits(natal_data, target_dt)
            
            # 3. Format Context
            context = f"Forecast/Transits for {person_name} on {target_dt.date()}:\n"
            if not forecast_data['aspects']:
                context += "No major planetary aspects detected for this date."
            else:
                for a in forecast_data['aspects']:
                    context += f"- Transit {a['transit_planet']} in {a['transit_sign']} makes {a['aspect']} to Natal {a['natal_planet']} (Orb: {a['orb_diff']}°)\n"
            return context

    def get_semantic_context(self, query: str, top_k: int = 3) -> str:
        """Fetches relevant text chunks from the vector index."""
        query_vector = self.intel.generate_embedding(query)
        if not query_vector:
            return "No semantic context found (Embedding failed)."

        cypher = """
        CALL db.index.vector.queryNodes('chunk_embeddings', $k, $vector)
        YIELD node, score
        RETURN node.text as text, score
        """
        with self.bridge.driver.session() as session:
            results = session.run(cypher, k=top_k, vector=query_vector).data()
            if not results:
                return "No semantic context found in the database."
            
            context = "Contextual Information (from Documents):\n"
            for i, r in enumerate(results, 1):
                context += f"Chunk {i} [Score: {r['score']:.2f}]: \"{r['text']}\"\n"
            return context

    def ask(self, user_query: str, person_name: Optional[str] = None) -> str:
        """The Central Agentic Loop: Synthesize Graph + Vector + Forecast + AI."""
        logger.info(f"🧠 Brain thinking about: {user_query}")
        
        # 1. Gather Context
        astro_context = ""
        forecast_context = ""
        
        if person_name:
            logger.info(f"🌌 Fetching Natal Data for {person_name}...")
            astro_context = self.get_astro_context(person_name)
            
            # Simple heuristic for Time-Traveler Mode
            time_keywords = ["2025", "2026", "2027", "previsão", "futuro", "amanhã", "forecast", "trânsito"]
            if any(k in user_query.lower() for k in time_keywords):
                logger.info("🕰️ Time-Traveler Mode Activated: Calculating Transits...")
                # Extract year if possible, else use current
                target_date = None
                for year in ["2025", "2026", "2027"]:
                    if year in user_query:
                        target_date = f"{year}-01-01T12:00:00"
                        break
                forecast_context = self.get_forecast_context(person_name, target_date)
        
        logger.info("🔎 Fetching Semantic Data (Vector)...")
        semantic_context = self.get_semantic_context(user_query)

        # 2. Synthesize
        prompt = f"""
        You are MENIR, the Celestial Hybrid Engine. 
        Your goal is to provide a deep, integrated answer using three distinct data sources:
        
        [ASTROLOGICAL NATAL CONTEXT (LOGICAL/GRAPH)]
        {astro_context if astro_context else 'None provided.'}
        
        [ASTROLOGICAL FORECAST/TRANSITS (DYNAMIC MATH)]
        {forecast_context if forecast_context else 'None provided for this query.'}
        
        [SEMANTIC CONTEXT (INTUITIVE/VECTOR)]
        {semantic_context}
        
        [USER QUESTION]
        {user_query}
        
        INSTRUCTIONS:
        - Integrate the findings. 
        - If someone's NATAL chart has specific patterns, and the TRANSITS trigger them, explain what is happening.
        - Cross-reference with the SEMANTIC context (the user's diary/notes) to see if their feelings match the astrology.
        - Be insightful, poetic yet technically accurate. Use "Poesia-Engenharia".
        - Respond in the language of the user question (Portuguese).
        """
        
        logger.info("🎨 Synthesizing Final Hybrid Insight...")
        response = self.intel.model.generate_content(prompt)
        return response.text

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Menir Brain - Hybrid Q&A")
    parser.add_argument("query", nargs='?', help="The question to ask Menir")
    parser.add_argument("--query", dest="query_flag", help="Alternative query flag")
    parser.add_argument("--person", help="Focus on a specific person's chart")
    
    args = parser.parse_args()
    final_query = args.query if args.query else args.query_flag
    
    if not final_query:
        parser.print_help()
        sys.exit(1)
    
    brain = MenirBrain()
    try:
        ans = brain.ask(final_query, args.person)
        print("\n" + "="*50)
        print("🌌 MENIR RESPONSE:")
        print("="*50)
        print(ans)
    finally:
        brain.close()
