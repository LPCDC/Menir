
import os
import sqlite3
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

DB_PATH = "menir_cache.db"
QUERY = "O que é Menir?"
ANSWER = "Menir é a Memória Digital Eterna (Mocked Cache)."

def inject():
    # 1. Get Embedding (Hoping this endpoint is alive)
    print("Generating Embedding...")
    try:
        vec = genai.embed_content(
            model="models/text-embedding-004",
            content=QUERY,
            task_type="retrieval_query"
        )['embedding']
    except Exception as e:
        print(f"Embedding Failed: {e}")
        # Mock embedding for testing logic if API fails totally
        vec = [0.1] * 768 
    
    # 2. Insert into DB
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT OR REPLACE INTO semantic_cache VALUES (?, ?, ?, ?)", 
                 (QUERY, json.dumps(vec), ANSWER, time.time()))
    conn.commit()
    print(f"Injected: '{QUERY}' -> '{ANSWER}'")
    conn.close()

if __name__ == "__main__":
    inject()
