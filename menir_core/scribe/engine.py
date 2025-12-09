import json
import os
import re
import uuid
import datetime
from typing import Dict, Any, List, Optional
from menir_core.rag.agent import NarrativeAgent

class PrivacyRouter:
    """
    Decides if a project or text is safe to send to external LLMs.
    Defense-in-Depth: Project Type + Content Scanning.
    """
    
    # Simple regex patterns for PII detection
    PII_PATTERNS = {
        "cpf": r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "cnpj": r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b",
        "bank_account": r"\b\d{4,5}-\d\b", # simplistic
        "sensitive_keywords": r"(?i)\b(itaú|bradesco|banco do brasil|fatura|boleto|cartão de crédito|senha)\b"
    }

    @staticmethod
    def is_safe(project_type: str, content: str = "") -> Dict[str, Any]:
        """
        Check if safe. Returns: { "safe": bool, "reason": str|None }
        """
        SAFE_TYPES = ["fiction", "personal_creative", "public_demo"]
        
        # 1. Project Type Check
        if project_type.lower() not in SAFE_TYPES:
            return {"safe": False, "reason": f"Project Type '{project_type}' is restricted."}
        
        # 2. Content Scanning (PII)
        for p_name, pattern in PrivacyRouter.PII_PATTERNS.items():
            if re.search(pattern, content):
                return {"safe": False, "reason": f"Possible PII detected: {p_name}"}
                
        return {"safe": True, "reason": None}

class ScribeEngine:
    """
    The "Scribe" engine: Text-to-Graph Proposal Generator.
    Now with Provenance & PII Safety.
    """

    def __init__(self, project_type: str = "fiction"):
        self.project_type = project_type
        self.privacy = PrivacyRouter()
        self.agent = None # Deferred init

    def generate_proposal(self, text: str, source_filename: str = "unknown") -> Dict[str, Any]:
        """
        Analyze text and return a Graph Proposal JSON.
        """
        # 1. Safety Check
        safety = self.privacy.is_safe(self.project_type, text)
        if not safety["safe"]:
            return {
                "status": "skipped",
                "reason": safety["reason"],
                "proposal": {}
            }

        # 2. Init Agent (Lazy Load)
        if not self.agent:
            try:
                self.agent = NarrativeAgent()
            except Exception as e:
                return {"status": "error", "error": f"Agent Init Failed: {e}"}

        # 3. Load Ontology
        ontology_path = os.path.join(os.path.dirname(__file__), "..", "ontology", "narrative.ttl")
        ontology_context = ""
        try:
            with open(ontology_path, "r", encoding="utf-8") as f:
                ontology_context = f.read()
        except Exception:
            ontology_context = "Ontology unavailable."

        prompt = f"""
        You are 'The Scribe'. Extract narrative entities from the text.
        
        ONTOLOGY:
        ```ttl
        {ontology_context}
        ```
        
        RULES:
        1. OUTPUT JSON ONLY.
        2. STRUCTURE:
           {{
             "nodes": [ {{ "label": "...", "properties": {{...}} }} ],
             "relationships": [ {{ "start": "...", "type": "...", "end": "..." }} ]
           }}
        3. STRICT SCHEMA adherence.
        
        TEXT:
        {text[:2000]}... (truncated)
        """
        
        try:
            response = self.agent.client.chat.completions.create(
                model=self.agent.model,
                messages=[
                    {"role": "system", "content": "You are a graph extraction engine. Output JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            content = response.choices[0].message.content
            raw_data = json.loads(content)
            
            # 4. Inject Metadata (Provenance)
            proposal_id = str(uuid.uuid4())
            timestamp = datetime.datetime.utcnow().isoformat() + "Z"
            
            enhanced_proposal = {
                "proposal_id": proposal_id,
                "source": {
                    "file": source_filename,
                    "project": self.project_type,
                    "timestamp": timestamp
                },
                "nodes": raw_data.get("nodes", []),
                "relationships": raw_data.get("relationships", [])
            }
            
            return {
                "status": "success",
                "proposal": enhanced_proposal
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def save_proposal(self, proposal: Dict[str, Any], filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(proposal, f, indent=2, ensure_ascii=False)
