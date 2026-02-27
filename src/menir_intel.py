import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def get_best_model():
    """Busca dinâmica do melhor modelo (Flash 2.5 ou similar)."""
    try:
        genai.configure(api_key=API_KEY)
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                if "flash" in m.name and "1.5" in m.name: return m.name
                if "flash" in m.name: return m.name
        return "gemini-1.5-flash"
    except:
        return "gemini-pro"

def analyze_document_content(text_content, filename):
    if not API_KEY: return json.dumps({"error": "No API Key"})
    
    model_name = get_best_model()
    model = genai.GenerativeModel(model_name)

    prompt = f"""
    ROLE: Senior Data Architect for 'Menir' (Personal Second Brain).
    TARGET ONTOLOGY (V5 - Solar System):
    - Root: Person 'Luiz'.
    - Nodes: Person, Company, Project, Document.
    - Edges: OWNS, FRIEND_OF, MANAGES, DESCRIBES, HIRED_FOR, SUPPLIES.
    
    INPUT FILE: "{filename}"
    TEXT CONTENT:
    {text_content[:8000]} # Limitado para caber no contexto
    
    TASK: Extract structured data into JSON.
    RULES:
    1. DOCUMENT: Always create a 'Document' node for this file.
    2. PROJECT: Identify the main Project (e.g., Tivoli). Update it with technical specs (area, location) found.
    3. COMPANIES: Identify suppliers/contractors. Create 'Company' nodes.
    4. CONTRACTS: If values (R$) or deadlines are found, add them as properties to the edge (e.g., HIRED_FOR {{budget: 50000}}).
    5. MEMORIES: Extract risks, warnings, or historic notes as 'props' on the Project or Document.
    
    STRICT JSON OUTPUT SCHEMA:
    {{
        "nodes": [
            {{ "label": "Document", "name": "{filename}", "props": {{ "type": "Technical/Contract", "date": "YYYY-MM-DD" }} }},
            {{ "label": "Project", "name": "Tivoli", "props": {{ "technical_summary": "...", "status": "Active" }} }}
        ],
        "edges": [
            {{ "source": "{filename}", "target": "Tivoli", "type": "DESCRIBES" }}
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        if not text.startswith("{"): raise ValueError("IA não gerou JSON válido")
        return text
    except Exception as e:
        return json.dumps({"error": f"IA Error: {str(e)}"})
