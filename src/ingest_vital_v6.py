import json
import os
from neo4j import GraphDatabase

# Configuration
URI = os.getenv("NEO4J_URI", "bolt://menir-db:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "menir123"))

USER_DATA_DIR = "/app/user_data" # Inside container
UNIVERSE_FILE = os.path.join(USER_DATA_DIR, "menir_universe.json")
PROFILE_FILE = os.path.join(USER_DATA_DIR, "user_profile.json")

def ingest_genesis():
    print(f"🔌 Connecting to {URI}...")
    driver = GraphDatabase.driver(URI, auth=AUTH)

    with driver.session() as session:
        # Load JSONs
        print("📂 Loading User Data...")
        with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
            universe = json.load(f)
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            profile = json.load(f)

        # ---------------------------------------------------------
        # 1. THE CORE (Root & Holding)
        # ---------------------------------------------------------
        print("🏗️ Building Core (Root + Holding)...")
        root = universe["root_entity"]
        holding = universe["holding_company"]

        session.run("""
            MERGE (u:User {id: $uid})
            SET u.name = $uname
            
            MERGE (c:Company {name: $cname})
            SET c.id = $cid
            
            MERGE (u)-[:OWNS]->(c)
        """, uid=root["id"], uname=root["name"], 
             cid=holding["id"], cname=holding["name"])

        # ---------------------------------------------------------
        # 2. THE ECOSYSTEM
        # ---------------------------------------------------------
        print("🌍 Building Ecosystem...")
        for item in universe["ecosystem"]:
             entity = item["entity"]
             etype = entity["type"]
             
             # CASE: MAU (Company)
             if etype == "Company":
                 # Create Company & Link from Holding
                 session.run("""
                    MATCH (h:Company {id: $hid})
                    MERGE (c:Company {name: $name})
                    SET c.owner = $owner
                    MERGE (h)-[:PROVIDES_SERVICE_TO]->(c)
                 """, hid=holding["id"], name=entity["name"], owner=entity.get("owner", ""))
                 
                 # Create Projects
                 if "projects" in item:
                     for proj in item["projects"]:
                         session.run("""
                            MATCH (h:Company {id: $hid})
                            MATCH (c:Company {name: $cname})
                            MERGE (p:Project {name: $pname})
                            SET p.type = $ptype
                            
                            MERGE (c)-[:OWNS]->(p)
                            MERGE (h)-[:MANAGES]->(p)
                         """, hid=holding["id"], cname=entity["name"], 
                              pname=proj["name"], ptype=proj["type"])

             # CASE: Tania (Person/Consultant)
             elif etype == "Person" and "projects" in item: # Distinguish from Newton check
                 session.run("""
                    MATCH (h:Company {id: $hid})
                    MERGE (p:Person {name: $name})
                    SET p.role = $role
                    MERGE (h)-[:CONSULTS_FOR]->(p)
                 """, hid=holding["id"], name=entity["name"], role=entity.get("role", ""))

                 if "projects" in item:
                     for proj in item["projects"]:
                         session.run("""
                            MATCH (person:Person {name: $pname_person})
                            MERGE (p:Project {name: $pname})
                            SET p.type = $ptype
                            MERGE (person)-[:MANAGES]->(p)
                         """, pname_person=entity["name"], pname=proj["name"], ptype=proj["type"])

             # CASE: LegalCase (Itaú)
             elif etype == "LegalCase":
                 session.run("""
                    MATCH (h:Company {id: $hid})
                    MERGE (l:LegalCase {name: $name})
                    SET l.status = $status, l.cognitive_tag = $tag
                    MERGE (h)-[:LITIGATES_AGAINST]->(l)
                 """, hid=holding["id"], name=entity["name"], 
                      status=entity.get("status"), tag=entity.get("cognitive_tag"))
                 
                 # Antagonists
                 if "antagonists" in item:
                     for antag_name in item["antagonists"]:
                         session.run("""
                            MATCH (l:LegalCase {name: $lname})
                            MERGE (p:Person {name: $pname})
                            MERGE (p)-[:INVOLVED_IN]->(l)
                         """, lname=entity["name"], pname=antag_name)

             # CASE: Book (Fiction)
             elif etype == "Book":
                 # Link from Root (User)
                 session.run("""
                    MATCH (u:User {id: $uid})
                    MERGE (b:Book {name: $name})
                    MERGE (u)-[:EDITS {role: 'Curator'}]->(b)
                 """, uid=root["id"], name=entity["name"])

                 # Collaborators
                 if "collaborators" in item:
                     for collab in item["collaborators"]:
                         session.run("""
                            MATCH (b:Book {name: $bname})
                            MERGE (p:Person {name: $pname})
                            SET p.role = $role
                            MERGE (p)-[:WRITES]->(b)
                         """, bname=entity["name"], pname=collab["name"], role=collab["role"])
                 
                 # Characters (Namespace Logic)
                 if "characters" in item:
                     universe_name = entity["name"] # Use Book Name as Universe
                     for char in item["characters"]:
                         session.run("""
                            MATCH (b:Book {name: $bname})
                            MERGE (c:Character {name: $cname, universe: $universe})
                            SET c.role = $role
                            MERGE (b)-[:HAS_CHARACTER]->(c)
                         """, bname=entity["name"], cname=char["name"], 
                              universe=universe_name, role=char["role"])

        # ---------------------------------------------------------
        # 3. THE LENSES
        # ---------------------------------------------------------
        print("🧠 Injecting Lenses...")
        lens_list = profile.get("professional_lenses", [])
        for lens in lens_list:
             session.run("""
                MATCH (u:User {id: $uid})
                MERGE (l:Lens {id: $lid})
                SET l.name = $lname, 
                    l.trigger_keywords = $keywords,
                    l.system_prompt_modifier = $prompt
                MERGE (u)-[:HAS_LENS]->(l)
             """, uid=profile["user_id"], lid=lens["id"], 
                  lname=lens["name"], keywords=lens["trigger_keywords"], 
                  prompt=lens["system_prompt_modifier"])

    driver.close()
    print("✅ GENESIS COMPLETE.")

if __name__ == "__main__":
    ingest_genesis()
