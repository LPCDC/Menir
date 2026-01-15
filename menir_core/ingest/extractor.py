import os
import json
import logging
import google.generativeai as genai
from openai import OpenAI
from tavily import TavilyClient

logger = logging.getLogger("menir_extractor")

class MenirExtractor:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        
        # Config Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            genai.configure(api_key=gemini_key)
            # Menir v4.1 Strategy: Prioritize Flash 2.0, fallback to 1.5
            try:
                # Assuming 2.0 string (actual slug needs verification, using experimental slug for now or user provided)
                # If model is not found, generation usually fails, not init. 
                # But we can set a primary and fallback string.
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp') 
                self.gemini_fallback = genai.GenerativeModel('gemini-1.5-flash')
            except:
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                self.gemini_fallback = None
        else:
            self.gemini_model = None
            self.gemini_fallback = None

        # Config OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
        else:
            self.openai_client = None

        # Config Tavily
        tavily_key = os.getenv("TAVILY_API_KEY")
        if tavily_key:
            self.tavily = TavilyClient(api_key=tavily_key)
        else:
            self.tavily = None
            logger.warning("TAVILY_API_KEY not found.")

    def extract_knowledge(self, text):
        prompt = f"""
        Analyze the following text and extract knowledge graph elements.
        Return ONLY a JSON object (no markdown, no extra text) with the following structure:
        {{
            "entities": [
                {{"name": "Entity Name", "label": "Person|Organization|Location|Concept|Tool", "description": "Brief description"}}
            ],
            "relationships": [
                {{"source": "Entity Name", "target": "Entity Name", "type": "RELATIONSHIP_TYPE", "description": "Context"}}
            ],
            "search_intents": ["List of things mentioned that require external fact-checking or more info"]
        }}

        TEXT:
        {text}
        """

        try:
            if self.provider == "openai" and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a knowledge extraction engine. Return valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                raw_json = response.choices[0].message.content
                return json.loads(raw_json)
            
            elif self.gemini_model:
                try:
                    response = self.gemini_model.generate_content(prompt)
                    raw_json = response.text.replace("```json", "").replace("```", "").strip()
                    return json.loads(raw_json)
                except Exception as e:
                    logger.warning(f"Gemini Primary Failed ({e}). Attempting Fallback...")
                    if self.gemini_fallback:
                        response = self.gemini_fallback.generate_content(prompt)
                        raw_json = response.text.replace("```json", "").replace("```", "").strip()
                        return json.loads(raw_json)
                    else:
                        raise e
            
            else:
                return {"error": f"LLM Provider {self.provider} not configured or missing key."}

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return {"entities": [], "relationships": [], "error": str(e)}

    def enrich_context(self, query):
        if not self.tavily:
            return None
        
        try:
            return self.tavily.search(query=query, search_depth="basic")
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return None
