
"""
Genesis Astro
Seeds the Menir Graph with Static Astrological Data.
Also introduces "Daniella Badinni" to the system.
"""
import logging
from src.v3.menir_bridge import MenirBridge
from .schema import CelestialBody, ZodiacSign, House
from src.v3.schema import Person

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GenesisAstro")

def seed_static_data(bridge: MenirBridge):
    """Creates Planets, Signs, and Houses."""
    project = "MenirAstro"
    
    # 1. Celestial Bodies
    bodies = [
        {"name": "Sun", "archetype": "The Hero/Central Self"},
        {"name": "Moon", "archetype": "The Mother/Emotional Body"},
        {"name": "Mercury", "archetype": "The Messenger/Intellect"},
        {"name": "Venus", "archetype": "The Lover/Values"},
        {"name": "Mars", "archetype": "The Warrior/Drive"},
        {"name": "Jupiter", "archetype": "The Sage/Expansion"},
        {"name": "Saturn", "archetype": "The Teacher/Restriction"},
        {"name": "Uranus", "archetype": "The Rebel/Change"},
        {"name": "Neptune", "archetype": "The Mystic/Illusion"},
        {"name": "Pluto", "archetype": "The Alchemist/Transformation"},
        {"name": "Chiron", "archetype": "The Wounded Healer"},
        {"name": "North Node", "archetype": "Destiny"},
        {"name": "South Node", "archetype": "Karma"}
    ]
    
    logger.info("🌌 Seeding Celestial Bodies...")
    for b in bodies:
        node = CelestialBody(name=b["name"], archetype=b["archetype"], project=project)
        bridge.merge_node(node)
        
    # 2. Zodiac Signs
    signs = [
        ("Aries", "Fire", "Cardinal", "Mars"),
        ("Taurus", "Earth", "Fixed", "Venus"),
        ("Gemini", "Air", "Mutable", "Mercury"),
        ("Cancer", "Water", "Cardinal", "Moon"),
        ("Leo", "Fire", "Fixed", "Sun"),
        ("Virgo", "Earth", "Mutable", "Mercury"),
        ("Libra", "Air", "Cardinal", "Venus"),
        ("Scorpio", "Water", "Fixed", "Mars/Pluto"),
        ("Sagittarius", "Fire", "Mutable", "Jupiter"),
        ("Capricorn", "Earth", "Cardinal", "Saturn"),
        ("Aquarius", "Air", "Fixed", "Saturn/Uranus"),
        ("Pisces", "Water", "Mutable", "Jupiter/Neptune")
    ]
    
    logger.info("♈ Seeding Zodiac Signs...")
    for s in signs:
        node = ZodiacSign(name=s[0], element=s[1], modality=s[2], ruler=s[3], project=project)
        bridge.merge_node(node)
        
    # 3. Houses
    logger.info("🏠 Seeding Houses...")
    house_domains = [
        "Identity", "Values", "Communication", "Home/Roots", "Creativity/Children", "Service/Health",
        "Relationships", "Transformation/Shared Assets", "Philosophy/Travel", "Career/Public Image",
        "Community/Hopes", "Subconscious/Closure"
    ]
    for i, domain in enumerate(house_domains, 1):
        node = House(number=i, domain=domain, project=project, name=f"House {i}") # Added name explicitly
        bridge.merge_node(node)

def ingest_daniella(bridge: MenirBridge):
    """Ingests User Request: Daniella Badinni."""
    logger.info("👤 Ingesting New Friend: Daniella Badinni...")
    daniella = Person(
        name="Daniella Badinni", 
        role="Friend", 
        is_real=True, 
        context="Real World", 
        project="MenirVital"
    )
    bridge.merge_node(daniella)
    logger.info("✅ Daniella is now in the Graph.")

def main():
    bridge = MenirBridge()
    try:
        seed_static_data(bridge)
        ingest_daniella(bridge)
        logger.info("✨ Genesis Complete.")
    finally:
        bridge.close()

if __name__ == "__main__":
    main()
