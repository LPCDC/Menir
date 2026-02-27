"""
Menir V4 - Semantic Memory (Semantic Caching)
Implements a local SQLite-Vector cache to reduce API costs and latency.
"""
import os
import time
import json
import logging
import sqlite3
import numpy as np
import google.generativeai as genai
from datetime import datetime, timedelta

# Silence TensorFlow warnings if present
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MenirMemory")

CACHE_DB = "menir_cache.db"
EMBEDDING_MODEL = "models/text-embedding-004"
SIMILARITY_THRESHOLD = 0.92  # High confidence only
CACHE_TTL_HOURS = 24

class MenirMemory:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Google API Key required for Memory Embeddings.")
        genai.configure(api_key=api_key)
        self.conn = self._init_db()

    def _init_db(self):
        """Initialize SQLite with semantic_cache table."""
        conn = sqlite3.connect(CACHE_DB, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS semantic_cache (
                query_text TEXT PRIMARY KEY,
                embedding_json TEXT,
                answer_text TEXT,
                created_at REAL
            )
        """)
        conn.commit()
        return conn

    def _get_embedding(self, text: str) -> list[float]:
        """Generate vector embedding using Gemini."""
        try:
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Embedding API Error: {e}")
            return None

    def _cosine_similarity(self, vec_a, vec_b):
        """Compute Cosine Similarity."""
        a = np.array(vec_a)
        b = np.array(vec_b)
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def prune_cache(self):
        """Remove expired entries (TTL)."""
        expiry = time.time() - (CACHE_TTL_HOURS * 3600)
        with self.conn:
            self.conn.execute("DELETE FROM semantic_cache WHERE created_at < ?", (expiry,))
        # logger.info("🧹 Memory Pruned (TTL Clean).")

    def search(self, query: str) -> str:
        """
        Search for a semantically similar query in cache.
        Returns cached answer if match > threshold.
        """
        self.prune_cache()
        
        # 1. Generate Query Embedding
        query_vec = self._get_embedding(query)
        if not query_vec:
            return None # Fail silently, proceed to live RAG

        # 2. Fetch Candidates
        cursor = self.conn.cursor()
        cursor.execute("SELECT query_text, embedding_json, answer_text FROM semantic_cache")
        rows = cursor.fetchall()
        
        # 3. Linear Scan (Fast enough for <10k rows)
        best_score = 0.0
        best_answer = None
        matched_query = None

        for q_text, embed_json, answer in rows:
            cached_vec = json.loads(embed_json)
            score = self._cosine_similarity(query_vec, cached_vec)
            
            if score > best_score:
                best_score = score
                best_answer = answer
                matched_query = q_text

        # 4. Threshold Check
        if best_score >= SIMILARITY_THRESHOLD:
            logger.info(f"⚡ Memory Hit! (Score: {best_score:.4f}) matched '{matched_query}'")
            return best_answer
        
        # logger.info(f"💨 Memory Miss (Best: {best_score:.4f}). Calling Gemini...")
        return None

    def store(self, query: str, answer: str):
        """Save query+answer to cache."""
        if not answer or "[AI OFFLINE]" in answer:
            return # Don't cache errors

        embedding = self._get_embedding(query)
        if not embedding:
            return
            
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO semantic_cache VALUES (?, ?, ?, ?)",
                (query, json.dumps(embedding), answer, time.time())
            )
        # logger.info("💾 Memory Updated.")

    def close(self):
        self.conn.close()
