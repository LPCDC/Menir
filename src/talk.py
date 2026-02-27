import os
import sys
import glob
import json
import google.generativeai as genai
from neo4j import GraphDatabase

# CONFIGURAÇÕES (Puxa do ambiente ou define fixo)
MY_KEY = "AIzaSyA0bSdQnAZqLtf0uXfgjVtIIeJmgOqTyes" # Sua Chave
NEO4J_URI = "bolt://menir-neo4j:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "menir123"
OUTBOX_DIR = "/app/data/outbox"

# Configura IA
genai.configure(api_key=MY_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def get_latest_dossier():
    """Pega o último arquivo processado (Memória de Curto Prazo)"""
    try:
        list_of_files = glob.glob(f'{OUTBOX_DIR}/*.md')
        if not list_of_files: return None
        latest_file = max(list_of_files, key=os.path.getctime)
        with open(latest_file, 'r', encoding='utf-8') as f:
            return f.read()
    except: return None

def query_memory(search_term):
    """Consulta o Neo4j (Memória de Longo Prazo)"""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        data = []
        with driver.session() as session:
            # Busca genérica por qualquer coisa parecida com o termo
            result = session.run("""
                MATCH (e:Entity)-[r]->(d:Document)
                WHERE e.name CONTAINS $term OR d.summary CONTAINS $term
                RETURN e.name, type(r), d.summary
                LIMIT 5
            """, term=search_term)
            for record in result:
                data.append(f"{record['e.name']} ({record['type(r)']}) no doc: {record['d.summary'][:100]}...")
        driver.close()
        return "\n".join(data)
    except: return ""

def main():
    print("\n" + "="*40)
    print("   ALÔ MENIR - CANAL DE COMANDO")
    print("="*40)
    print("Digite 'sair' para fechar.\n")

    # Contexto Inicial
    latest = get_latest_dossier()
    if latest:
        print(f" [Contexto Ativo]: Último arquivo processado carregado na memória.\n")
    
    history = []

    while True:
        user_input = input("VOCÊ: ")
        if user_input.lower() in ['sair', 'exit', 'tchau']: break
        
        # Monta o Prompt Dinâmico
        prompt_parts = ["Você é o Menir, um assistente pessoal inteligente."]
        
        # 1. Injeta Memória Recente
        if latest:
            prompt_parts.append(f"CONTEXTO RECENTE (Último Arquivo):\n{latest}")
        
        # 2. Injeta Histórico da Conversa
        if history:
            prompt_parts.append(f"HISTÓRICO:\n{history[-3:]}")

        # 3. Tenta buscar Memória Longa se o usuário perguntar de alguém específico
        # (Lógica simples: se tem letra maiúscula, tenta buscar no banco)
        potential_entities = [w for w in user_input.split() if w[0].isupper() and len(w)>3]
        for ent in potential_entities:
            mem = query_memory(ent)
            if mem: prompt_parts.append(f"MEMÓRIA DE LONGO PRAZO SOBRE '{ent}':\n{mem}")

        # 4. A Pergunta
        prompt_parts.append(f"USUÁRIO: {user_input}")
        prompt_parts.append("MENIR (Seja direto e útil):")

        # Gera Resposta
        try:
            response = model.generate_content(prompt_parts)
            reply = response.text
            print(f"\nMENIR: {reply}\n")
            print("-" * 40)
            history.append(f"User: {user_input}\nMenir: {reply}")
        except Exception as e:
            print(f" Erro de conexão: {e}")

if __name__ == "__main__":
    main()
