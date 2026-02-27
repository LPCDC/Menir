# src/v3/menir_intel.py
import os
import json
import logging
import warnings
import unidecode

# Suppress Google GenAI deprecation warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
warnings.filterwarnings("ignore", category=UserWarning, module="google.generativeai")

import google.generativeai as genai
from unidecode import unidecode

logger = logging.getLogger(__name__)

class MenirIntel:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is missing.")
        # Configure API
        genai.configure(api_key=api_key)
        
        # Use available model (Updated to alias for stability)
        self.model = genai.GenerativeModel('gemini-flash-latest')
        
        # V3 Spec: Allowlist (Advanced Ontology)
        self.ALLOWED_LABELS = {
            "Person", "Organization", "Location", "Role", 
            "DocumentConcept", "Asset", "Event", "Obligation", "Risk",
            "Concept", "Year", "Month", "Day"
        }

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generates 768-dim vector using Gemini text-embedding-004.
        """
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document" # Optimized for storage
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Embedding Gen Error: {e}")
            return None

    def _sanitize_label(self, label):
        """Converte para PascalCase e valida contra Allowlist."""
        # Remove caracteres especiais e espaços
        clean = "".join(x for x in unidecode(label).title() if x.isalnum())
        
        # Mapeamentos comuns (Opcional - pode ser expandido)
        if clean in ["Empresa", "Company"]: return "Organization"
        if clean in ["Pessoa", "Individuo"]: return "Person"
        
        if clean in self.ALLOWED_LABELS:
            return clean
        return "DocumentConcept" # Fallback seguro ou raise Error

    def _truncate_props(self, props):
        """Trunca valores de string > 1000 chars e remove nulos."""
        clean_props = {}
        for k, v in props.items():
            if v is None or v == "" or v == "N/A":
                continue
            if isinstance(v, str):
                if len(v) > 1000:
                    v = v[:1000] + "..."
                clean_props[k] = v
            else:
                clean_props[k] = v
        return clean_props

    def extract(self, text, project_name, doc_hash):
        """
        Extrai grafo, valida schema e injeta escopo (Project/Hash).
        """
        system_prompt = """
        Você é um extrator de grafos estrito de Ontologia Avançada (BFO/SKOS/Time/PROV-O).
        Saída OBRIGATÓRIA: JSON válido.
        Schema:
        {
            "nodes": [{"label": "PascalCase", "name": "string", "properties": {}}],
            "edges": [{"type": "UPPER_SNAKE_CASE", "from": "string", "to": "string", "properties": {}}]
        }
        Regras Ontológicas Rígidas:
        1. TEMPO: Extraia datas como nós separados: "Year" (ex: "2026"), "Month" (ex: "2"), "Day" (ex: "15"). Relacione-os usando HAS_MONTH e HAS_DAY.
        2. EVENTOS: Tudo que "acontece" deve ser um nó "Event" (ex: "Assinatura do Contrato", "Transição").
        3. CONCEITOS: Ideias abstratas e áreas de estudo devem ser nós "Concept" (ex: "Filosofia", "Linguística").
        4. PROCEDÊNCIA: Conecte as pessoas aos eventos via PARTICIPATED_IN (não ligue pessoas direto a empresas, aponte para um Evento que aponta para a empresa).
        5. Labels permitidos: Person, Organization, Location, Role, Asset, Event, Risk, Concept, Year, Month, Day.
        6. Não crie nós para o documento atual em si (o sistema fará isso via PROV-O no backend).
        """
        
        try:
            response = self.model.generate_content(
                f"{system_prompt}\n\nTEXTO:\n{text}",
                generation_config={"response_mime_type": "application/json"}
            )
            
            raw_data = json.loads(response.text)
            
            # Pós-processamento e Injeção de Escopo
            processed_nodes = []
            processed_edges = []
            
            # Set para validação de orfãos
            node_names = set()

            for n in raw_data.get("nodes", []):
                label = self._sanitize_label(n.get("label", "Concept"))
                name = n.get("name", "Unknown").strip()
                name_key = unidecode(name).lower().strip()
                
                if not name: continue
                
                node_names.add(name)
                
                processed_nodes.append({
                    "label": label,
                    "name": name,
                    "name_key": name_key, # Identidade interna
                    "project": project_name, # Escopo Injetado
                    "doc_sha256": doc_hash,  # Escopo Injetado
                    "properties": self._truncate_props(n.get("properties", {}))
                })

            for e in raw_data.get("edges", []):
                src = e.get("from", "").strip()
                tgt = e.get("to", "").strip()
                
                # Check de Orfãos (Integridade V3)
                if src not in node_names or tgt not in node_names:
                    logger.warning(f"Skipping orphan edge: {src} -> {tgt}")
                    continue

                processed_edges.append({
                    "type": unidecode(e.get("type", "RELATED_TO")).upper().replace(" ", "_"),
                    "from_key": unidecode(src).lower().strip(),
                    "to_key": unidecode(tgt).lower().strip(),
                    "project": project_name, # Escopo Injetado
                    "doc_sha256": doc_hash,  # Escopo Injetado
                    "properties": self._truncate_props(e.get("properties", {}))
                })

            return {"nodes": processed_nodes, "edges": processed_edges, "project": project_name, "doc_sha256": doc_hash}

        except Exception as e:
            logger.error(f"AI Extraction Failed: {e}")
            raise
