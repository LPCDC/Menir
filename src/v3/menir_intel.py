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
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_exponential, retry_if_exception_type, before_sleep_log

logger = logging.getLogger(__name__)

class MenirIntel:
    def __init__(self, api_key: str = None):
        """
        Inicializa o MenirIntel com suporte a Dual-Boot:
        1. Enterprise (nFADP Compliance): Se VERTEX_PROJECT_ID existir, usa o Google Cloud em Zurique.
        2. Development: Fallback para a API pública do Gemini (genai) usando GOOGLE_API_KEY.
        """
        self.is_enterprise = False
        vertex_project = os.getenv("VERTEX_PROJECT_ID")
        
        if vertex_project:
            logger.info("🛡️ [nFADP Compliance] Explicit Enterprise Configuration Detected. Booting Vertex AI in europe-west6...")
            try:
                import vertexai
                from vertexai.generative_models import GenerativeModel
                # Force Switzerland/Europe location for Data Residency
                vertexai.init(project=vertex_project, location="europe-west6")
                self.model = GenerativeModel("gemini-1.5-pro-001")
                self.is_enterprise = True
                logger.info("✅ Vertex AI Enterprise Endpoint connected.")
            except ImportError:
                raise ImportError("A biblioteca 'google-cloud-aiplatform' não está instalada. Execute 'pip install google-cloud-aiplatform' para compliance enterprise.")
        else:
            if not api_key:
                api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("Nenhum VERTEX_PROJECT_ID ou GOOGLE_API_KEY fornecido. O Motor Intelectual não pode inicializar.")
                
            logger.warning("⚠️ [Development Mode] Inicializando Gemini API Pública. Não processar dados PII sensíveis nFADP aqui.")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # V3 Spec: Allowlist (Advanced Ontology)
        self.ALLOWED_LABELS = {
            "Person", "Organization", "Location", "Role", 
            "DocumentConcept", "Asset", "Event", "Obligation", "Risk",
            "Concept", "Year", "Month", "Day"
        }

    @retry(
        stop=(stop_after_attempt(3) | stop_after_delay(60)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def generate_embedding(self, text: str) -> list[float]:
        """
        Generates 768-dim vector using Gemini text-embedding-004.
        """
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document", # Optimized for storage
                request_options={"timeout": 60.0}
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Embedding Gen Error: {e}")
            return None

    @retry(
        stop=(stop_after_attempt(3) | stop_after_delay(60)),
        wait=wait_exponential(multiplier=2, min=4, max=15),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def structured_inference(self, prompt: str, image_path: str = None, response_schema=None):
        """
        Inferência Bimodal Unificada e Agnóstica baseada em Schema Pydantic.
        Substitui a antiga ontologia fixa BFO/SKOS, servindo a qualquer Skill de Extração nativamente.
        """
        import asyncio
        contents = [prompt]
        
        if image_path and os.path.exists(image_path):
            try:
                from PIL import Image
                img = Image.open(image_path)
                contents.append(img)
            except Exception as e:
                logger.error(f"Erro ao carregar imagem bimodal para Vision LLM: {e}")
                raise
                
        if response_schema:
            schema_json = response_schema.model_json_schema()
            contents[0] += f"\n\nInstrução Mandatória: Retorne APENAS um JSON válido que obedeça ESTRITAMENTE a este Schema. O output tem de ser nativo, cru, e exato:\n{json.dumps(schema_json, ensure_ascii=False)}"
            
        generation_config = {"response_mime_type": "application/json"}
        
        try:
            # Envolve a inferência em I/O Thread para evitar Starvation no AsyncRunner Event Loop
            response = await asyncio.to_thread(
                self.model.generate_content,
                contents,
                generation_config=generation_config
            )
            
            raw_text = response.text
            
            # Limpar blocos encadeados de markdown se a API ignorar o mime_type e vomitar backticks.
            if raw_text.startswith("```"):
                lines = raw_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_text = "\n".join(lines).strip()
                
            json_response = json.loads(raw_text)
            
            # Autoproofing do Pydantic Typecasting
            if response_schema:
                return response_schema.model_validate(json_response)
                
            return json_response
            
        except json.JSONDecodeError as j_err:
            logger.error(f"AI Structured Inference Parsing Failed (JSON format error): {j_err} | Text: {raw_text}")
            raise ValueError(f"O modelo injetou quebra de formatação: {j_err}")
        except Exception as e:
            logger.error(f"AI Structured Inference Final Execution Failed: {e}")
            raise
