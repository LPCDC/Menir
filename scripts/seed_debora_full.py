#!/usr/bin/env python3
"""
seed_debora_full.py — Master ingestion for Better in Manhattan Chapter 1.
Combines PDF text analysis + Instagram metadata + Neo4j graph construction.
"""

import os
import logging
from datetime import datetime
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Tenta importar o sistema de log do Menir
try:
    from menir10.menir10_log import append_log, make_entry
except ImportError:
    # Fallback apenas para não quebrar se o path estiver errado
    print("⚠️  Aviso: Módulo menir10 não encontrado. Logs serão apenas impressos.")
    def append_log(entry): print(f"[LOG SIMULADO] {entry}")
    def make_entry(**kwargs): return kwargs

# Configuração
logging.basicConfig(level=logging.INFO)
load_dotenv()

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "menir123"))
PROJECT_ID = "livro_debora_cap1"

# --- DADOS BRUTOS (Extraídos da sua análise do PDF e Imagens) ---

# 1. O Texto do Capítulo 1 (Resumo estruturado dos eventos principais do PDF)
CAP1_SUMMARY = """
263 dias para as férias de verão. Manhã de setembro. Caroline acorda com 'Here Comes the Sun'.
Café da manhã com Olivia (governanta). Pai (Nicholas) saiu cedo, deixou bilhete chamando-a de 'tiptoe'.
Mãe (Beatrice) aparece brevemente. Andy (motorista) leva Carol para Trailblazer Academy.
Encontro com Lauren. Spencer não responde. Diretor Smith dá boas-vindas.
Aula de Ed. Física com Sr. O'Donnel. Dean Bellini chega atrasado e flerta.
Almoço: Dean convida para festa sexta-feira. Menção ao primeiro beijo de Carol com Spencer (oitava série).
Dean revela fofoca: Lauren e Matt estão namorando. Carol fica chocada e finge cólica para ir embora.
Spencer aparece no apartamento de Carol. Reencontro caloroso ("girou no ar").
Spencer confirma namoro de Lauren/Matt. Lauren chega para se explicar.
Piquenique no Central Park com Spencer. Quase beijo. Clima estranho.
Sexta-feira: Festa na casa de Dean. Carol bebe. Spencer chega estilo 'Teen Vogue'.
Dormem na casa de Spencer. Sábado: Madame Tussauds, Starbucks.
Noite de filmes na casa de Spencer ('Garota Mimada'). Segundo 'quase beijo'. Constrangimento.
Terça-feira seguinte: Carol acerta bolada em Luc (novato francês). Luc revela ser amigo de Spencer.
Lauren anuncia festa no 'The Empire'.
"""

# 2. Dados dos Personagens (Instagram + Texto)
CHARACTERS = [
    {
        "id": "caroline_howell", "name": "Caroline Howell", "role": "Protagonist",
        "archetype": "Home Maker / The Heart", "visual": ["ruiva", "cozy", "blue_pastel"],
        "traits": ["Acolhedora", "Sensível", "Observadora"]
    },
    {
        "id": "spencer_wolfgang", "name": "Spencer Wolfgang", "role": "Love Interest",
        "archetype": "Broken Boy / Bad Boy Redemption", "visual": ["leather_jacket", "messy_hair", "intense_eyes"],
        "traits": ["Inquieto", "Protetor", "Dualidade"]
    },
    {
        "id": "lauren_beaumont", "name": "Lauren Beaumont", "role": "Best Friend",
        "archetype": "The Socialite with Purpose", "visual": ["beret", "it_girl", "blonde"],
        "traits": ["Autêntica", "Estratégica", "Leal"]
    },
    {
        "id": "dean_bellini", "name": "Dean Bellini", "role": "Catalyst",
        "archetype": "The Controller", "visual": ["polo_shirt", "clean_cut", "watch"],
        "traits": ["Perspicaz", "Provocador", "Dominante"]
    },
    {
        "id": "luc_french", "name": "Luc", "role": "New Friend",
        "archetype": "The Friendly Outsider", "visual": ["casual", "french_charm"],
        "traits": ["Gentil", "Aberto"]
    }
]

def run_seed():
    print(f"🚀 Iniciando Ingestão para {PROJECT_ID}...")
    
    # 1. Criar Artefato de Texto
    art_path = "artifacts/debora/cap1_summary.txt"
    with open(art_path, "w") as f:
        f.write(CAP1_SUMMARY)
    print(f"📄 Texto do Capítulo 1 salvo em {art_path}")

    # 2. Conectar ao Neo4j
    try:
        driver = GraphDatabase.driver(URI, auth=AUTH)
        driver.verify_connectivity()
    except Exception as e:
        print(f"❌ Erro de conexão Neo4j: {e}")
        return

    with driver.session() as session:
        # 3. Criar Livro e Autora
        print("🌱 Criando Autora e Livro...")
        session.run("""
            MERGE (a:Author {id: 'debora_vezzali'})
            SET a.name = 'Débora Vezzali', a.mbti = 'INFJ-T', a.house = 'Hufflepuff'
            
            MERGE (b:Book {id: 'better_in_manhattan'})
            SET b.title = 'Better in Manhattan', b.genre = 'YA Contemporary'
            
            MERGE (a)-[:AUTHORED]->(b)
        """)

        # 4. Criar Personagens (Nodes + Visual Tags)
        print("🎭 Inserindo Elenco e Tags Visuais...")
        for char in CHARACTERS:
            session.run("""
                MERGE (c:Character {id: $id})
                SET c.name = $name, c.role = $role, c.archetype = $archetype, c.psych_trait = $traits
                
                WITH c
                MATCH (b:Book {id: 'better_in_manhattan'})
                MERGE (c)-[:APPEARS_IN]->(b)
            """, id=f"char:{char['id']}", name=char['name'], role=char['role'], 
                 archetype=char['archetype'], traits=char['traits'])
            
            # Tags Visuais como nós separados (para busca vetorial futura)
            for tag in char['visual']:
                session.run("""
                    MATCH (c:Character {id: $id})
                    MERGE (t:VisualTag {name: $tag})
                    MERGE (c)-[:HAS_VISUAL]->(t)
                """, id=f"char:{char['id']}", tag=tag)

        # 5. Criar Eventos da Timeline (Básico)
        print("⏳ Construindo Timeline Inicial...")
        timeline_events = [
            ("evt:start_school", "Terça-feira: Início das aulas e revelação do namoro Lauren/Matt"),
            ("evt:park_picnic", "Terça-feira (Tarde): Piquenique e quase beijo no parque"),
            ("evt:dean_party", "Sexta-feira: Festa na casa de Dean"),
            ("evt:movie_night", "Sábado: Noite de filmes e segundo quase beijo"),
            ("evt:luc_incident", "Terça seguinte: Bolada no Luc e apresentação")
        ]
        
        prev_evt = None
        for eid, desc in timeline_events:
            session.run("""
                MERGE (e:TimelineEvent {id: $id})
                SET e.description = $desc, e.project_id = $pid
                
                WITH e
                MATCH (b:Book {id: 'better_in_manhattan'})
                MERGE (e)-[:PART_OF_STORY]->(b)
            """, id=eid, desc=desc, pid=PROJECT_ID)
            
            if prev_evt:
                session.run("""
                    MATCH (e1:TimelineEvent {id: $prev}), (e2:TimelineEvent {id: $curr})
                    MERGE (e1)-[:NEXT]->(e2)
                """, prev=prev_evt, curr=eid)
            prev_evt = eid

    driver.close()
    print("✅ Grafo Populado com Sucesso.")

    # 6. Log no Event Sourcing (Menir Core)
    try:
        log_entry = make_entry(
            project_id=PROJECT_ID,
            intent_profile="seed_ingestion",
            flags={"success": True, "source": "pdf_and_instagram"},
            metadata={
                "chars_ingested": len(CHARACTERS),
                "timeline_events": len(timeline_events),
                "note": "Initial Full Seed of Chapter 1 + Instagram Metadata"
            }
        )
        append_log(log_entry)
        print("📝 Evento registrado no Log JSONL.")
    except Exception as e:
        print(f"⚠️ Erro ao gravar log: {e}")

if __name__ == "__main__":
    run_seed()
