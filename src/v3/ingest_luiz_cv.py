import logging
from src.v3.menir_bridge import MenirBridge
from src.v3.tenant_middleware import current_tenant_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IngestCV")

def ingest_cv():
    bridge = MenirBridge()
    query = """
    // 1. Root Person Update
    MERGE (luiz:Person:Root {name: 'Luiz'})
    SET luiz.full_name = 'Luiz Paulo Carvalho de Carvalho',
        luiz.title = 'Jornalista / Tradutor / Copywriter',
        luiz.english_level = 'Extremely Advanced',
        luiz.hobbies = ['Musician (Jazz/Blues Guitar)', 'Avid Gamer (Ultima Online)']

    // 2. Education
    MERGE (usp:EducationalInstitution {name: 'USP - Universidade de São Paulo'})
    MERGE (casper:EducationalInstitution {name: 'Fundação Cásper Líbero'})
    
    MERGE (luiz)-[:STUDIED {
        degree: 'Ciências Sociais',
        start_year: 2001,
        end_year: 2003
    }]->(usp)

    MERGE (luiz)-[:STUDIED {
        degree: 'Jornalismo',
        start_year: 2001,
        end_year: 2005
    }]->(casper)
    
    // 3. Extracurriculars
    MERGE (cultura:EducationalInstitution {name: 'Cultura Inglesa'})
    MERGE (luiz)-[:STUDIED {
        degree: 'CPE / FCE (Complete Course)',
        start_year: 1992,
        end_year: 2000
    }]->(cultura)
    
    MERGE (iel:EducationalInstitution {name: 'Instituto de Estudos da Linguagem - USP'})
    MERGE (luiz)-[:STUDIED {
        degree: 'Tradução e Linguística',
        start_year: 2002
    }]->(iel)
    
    MERGE (pepperdine:EducationalInstitution {name: 'Pepperdine University (Los Angeles)'})
    MERGE (luiz)-[:STUDIED {
        degree: 'Intercâmbio (British and Commonwealth Literature)',
        start_year: 1996,
        duration: '3 meses'
    }]->(pepperdine)

    // 4. Experience
    MERGE (reword:Company {name: 'Reword'})
    MERGE (luiz)-[:WORKED_AT {
        role: 'Co-Fundador / Tradutor / Jornalista',
        start_year: 2014,
        end_year: 2023,
        description: 'Consultoria linguística, SEO, traduções corporativas, Press Release para grandes marcas (Artplan, Editora Record, etc).'
    }]->(reword)
    
    MERGE (howdy:Company {name: 'Howdy Toons'})
    MERGE (luiz)-[:WORKED_AT {
        role: 'Tradutor / Músico',
        start_year: 2017,
        end_year: 2018,
        description: 'Traduções de peças musicais e tutoria de cantores.'
    }]->(howdy)

    MERGE (record:Company {name: 'Editora Record'})
    MERGE (luiz)-[:WORKED_AT {
        role: 'Tradutor (Freelancer)',
        start_year: 2017,
        end_year: 2018,
        description: 'Tradução do romance O Colecionador de Peles (Jeff Deaver).'
    }]->(record)

    MERGE (mises:Company {name: 'Editora Mises'})
    MERGE (luiz)-[:WORKED_AT {
        role: 'Tradutor (Freelancer)',
        start_year: 2017,
        end_year: 2018,
        description: 'Tradução de Rumo a Uma Sociedade Libertária (Walter Block).'
    }]->(mises)

    MERGE (realejo:Company {name: 'Realejo Livraria'})
    MERGE (luiz)-[:WORKED_AT {
        role: 'Vendedor',
        start_year: 2014,
        duration: '6 meses',
        description: 'Livraria vintage. Sugestão de títulos, organização de eventos culturais e atendimento.'
    }]->(realejo)

    MERGE (amazon:Company {name: 'Amazon.com'})
    MERGE (luiz)-[:WORKED_AT {
        role: 'Redator JR (Freelancer)',
        start_year: 2012,
        end_year: 2013,
        description: 'Criação de resenhas de livros/filmes/álbuns, foco em conversão e anúncios.'
    }]->(amazon)

    MERGE (abril:Company {name: 'Editora Abril (Revista Exame)'})
    MERGE (luiz)-[:WORKED_AT {
        role: 'Art Buyer',
        start_year: 2011,
        end_year: 2012,
        description: 'Coordenação de pré-produção, compra de arte, seleção de fotógrafos e licenciamento de direitos.'
    }]->(abril)

    MERGE (dialeto:Company {name: 'Dialeto Social Media'})
    MERGE (luiz)-[:WORKED_AT {
        role: 'Web Content Assistant',
        start_year: 2009,
        duration: '8 meses',
        description: 'Blog posts para Nivea, Lenovo.'
    }]->(dialeto)

    MERGE (hotelier:Company {name: 'Hotelier News'})
    MERGE (luiz)-[:WORKED_AT {
        role: 'Jornalista',
        start_year: 2008,
        end_year: 2009,
        description: 'Escrita criativa para hotéis de luxo e guias turísticos.'
    }]->(hotelier)

    MERGE (meli:Company {name: 'Mercado Livre'})
    MERGE (luiz)-[:WORKED_AT {
        role: 'Estagiário (Trust & Safety)',
        start_year: 2006,
        end_year: 2007,
        description: 'Prevenção a fraudes, avaliações de risco e investigações de comunidade.'
    }]->(meli)
    """
    
    with bridge.driver.session() as session:
        token = current_tenant_id.set("root_admin")
        try:
            session.run(query)
            logger.info("✅ Luiz's CV Ingested Successfully.")
        finally:
            current_tenant_id.reset(token)
        
    bridge.close()

if __name__ == "__main__":
    ingest_cv()
