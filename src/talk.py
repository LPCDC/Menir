"""
talk.py — Interface de Consulta ao Grafo Menir
AVISO: Este módulo é legado e será substituído por uma MCP Tool na Seção B.
       Mantido aqui apenas para compatibilidade operacional imediata.
"""

import os
import logging
from dotenv import load_dotenv
from neo4j import GraphDatabase
from google import genai as genai_client

load_dotenv()

logger = logging.getLogger("menir.talk")

# --- Configuração via ambiente (NUNCA hardcode) ---
NEO4J_URI  = os.getenv("NEO4J_URI",  "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD") or os.getenv("NEO4J_PWD")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OUTBOX_DIR = os.getenv("MENIR_OUTBOX_DIR", "Menir_Outbox")

if not NEO4J_PASS:
    raise ValueError("NEO4J_PASSWORD não definido no .env")
if not GEMINI_KEY:
    raise ValueError("GEMINI_API_KEY não definido no .env")

_client = genai_client.Client(api_key=GEMINI_KEY)


def query_memory(search_term: str) -> str:
    """Consulta o Grafo Neo4j por contexto relacionado ao termo."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    try:
        data = []
        with driver.session() as session:
            result = session.run(
                """
                MATCH (n)
                WHERE toLower(n.name) CONTAINS toLower($term)
                   OR toLower(n.description) CONTAINS toLower($term)
                RETURN labels(n)[0] AS type, n.name AS name,
                       n.description AS desc
                LIMIT 10
                """,
                term=search_term
            )
            for record in result:
                data.append(f"[{record['type']}] {record['name']}: {record['desc']}")
        return "\n".join(data) if data else "Nenhum contexto encontrado no Grafo."
    except Exception:
        logger.exception(f"Falha ao consultar memória para: {search_term}")
        return ""
    finally:
        driver.close()


def get_latest_dossier(outbox_dir: str = OUTBOX_DIR) -> str:
    """Lê o dossier mais recente da pasta de saída."""
    try:
        files = sorted(
            [f for f in os.listdir(outbox_dir) if f.endswith(".txt")],
            reverse=True
        )
        if not files:
            return ""
        with open(os.path.join(outbox_dir, files[0]), "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        logger.exception(f"Falha ao ler dossier em: {outbox_dir}")
        return ""


def chat(user_input: str) -> str:
    """Consulta o Grafo e gera resposta contextualizada via Gemini."""
    memory = query_memory(user_input)
    dossier = get_latest_dossier()

    prompt = f"""Você é o assistente do sistema Menir, especializado em
contabilidade e gestão de documentos financeiros suíços.

CONTEXTO DO GRAFO:
{memory}

DOSSIER RECENTE:
{dossier}

PERGUNTA DO OPERADOR:
{user_input}

Responda de forma precisa e objetiva."""

    try:
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception:
        logger.exception("Falha na chamada ao Gemini em talk.chat()")
        return "Erro ao processar consulta."


if __name__ == "__main__":
    print("Menir Talk Interface (Legado)")
    print("AVISO: Use as MCP Tools via Synapse para acesso seguro multi-tenant.")
    while True:
        try:
            user_input = input("\\nVocê: ").strip()
            if user_input.lower() in ["sair", "exit", "quit"]:
                break
            response = chat(user_input)
            print(f"\\nMenir: {response}")
        except KeyboardInterrupt:
            break
