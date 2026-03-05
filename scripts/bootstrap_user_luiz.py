import os
import sys
from dotenv import load_dotenv

load_dotenv(override=True)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.v3.core.neo4j_pool import get_shared_driver

def run_cypher():
    driver = get_shared_driver()
    queries = [
        # NÓ RAIZ 1: Menir (já existe via bootstrap_system_graph)
        """MERGE (menir:Menir {uid: "MENIR_CORE"}) SET menir.version = "5.2", menir.updated_at = datetime()""",
        
        # NÓ RAIZ 2: User
        """MERGE (u:User:Person {uid: "luiz"}) SET u.name = "Luiz", u.role = "OWNER", u.city = "Santos", u.country = "BR", u.timezone = "America/Sao_Paulo", u.languages = ["pt-BR", "en", "de"], u.created_at = datetime()""",
        
        # RELAÇÃO BIDIRECIONAL DE GÊNESE
        """MATCH (menir:Menir {uid:"MENIR_CORE"}) MATCH (u:User {uid:"luiz"}) MERGE (menir)-[:SERVES_USER]->(u) MERGE (u)-[:IS_SERVED_BY]->(menir)""",
        
        # PROJETOS ATIVOS
        """MERGE (p1:Project {uid:"project_menir"}) SET p1.name = "Menir OS", p1.status = "ACTIVE", p1.priority = "CRITICAL" WITH p1 MATCH (u:User {uid:"luiz"}) MERGE (u)-[:OWNS_PROJECT]->(p1)""",
        """MERGE (p2:Project {uid:"project_refaz"}) SET p2.name = "REFAZ", p2.status = "FROZEN", p2.domain = "education" WITH p2 MATCH (u:User {uid:"luiz"}) MERGE (u)-[:OWNS_PROJECT]->(p2)""",
        """MERGE (p3:Project {uid:"project_talks"}) SET p3.name = "Talks Corporativos", p3.status = "FROZEN", p3.domain = "consulting" WITH p3 MATCH (u:User {uid:"luiz"}) MERGE (u)-[:OWNS_PROJECT]->(p3)""",
        """MERGE (p4:Project {uid:"project_tese"}) SET p4.name = "Sinfonia do Abandono", p4.domain = "academic", p4.subjects = ["Mario de Andrade", "Orson Welles"] WITH p4 MATCH (u:User {uid:"luiz"}) MERGE (u)-[:AUTHORED]->(p4)""",
        
        # COLABORADORES
        """MERGE (c1:Person {uid:"daniela_badin"}) SET c1.name = "Daniela Badin", c1.domain = "education" WITH c1 MATCH (u:User {uid:"luiz"}) MERGE (u)-[:COLLABORATES_WITH {project:"REFAZ"}]->(c1)""",
        """MERGE (c2:Person {uid:"ana_caroline"}) SET c2.name = "Ana Caroline Albuquerque", c2.domain = "consulting" WITH c2 MATCH (u:User {uid:"luiz"}) MERGE (u)-[:COLLABORATES_WITH {project:"Talks"}]->(c2)""",
        
        # FAMÍLIA / REDE BECO
        """MERGE (ap:Person {uid:"ana_paula"}) SET ap.name = "Ana Paula", ap.relation = "prima" WITH ap MATCH (u:User {uid:"luiz"}) MERGE (u)-[:FAMILY_OF]->(ap)""",
        """MERGE (ni:Person {uid:"nicole_beco"}) SET ni.name = "Nicole", ni.relation = "afilhada" WITH ni MATCH (u:User {uid:"luiz"}) MERGE (u)-[:GODFATHER_OF]->(ni)""",
        
        # CONECTAR FAMÍLIA AO TENANT BECO (sem vazar dados)
        """MATCH (ap:Person {uid:"ana_paula"}) MATCH (t:Tenant {name:"BECO"}) MERGE (ap)-[:OPERATES]->(t)""",
        """MATCH (ni:Person {uid:"nicole_beco"}) MATCH (t:Tenant {name:"BECO"}) MERGE (ni)-[:OPERATES]->(t)""",
        
        # CONSTRAINT DE UNICIDADE DO USER
        """CREATE CONSTRAINT user_uid_unique IF NOT EXISTS FOR (u:User) REQUIRE u.uid IS UNIQUE"""
    ]

    with driver.session() as session:
        for q in queries:
            session.run(q)
    print("✅ Bootstrap do Grafo Pessoal de Luiz e Hub de Metacognição finalizado com sucesso.")

if __name__ == "__main__":
    run_cypher()
