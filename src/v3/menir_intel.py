# src/v3/menir_intel.py
import json
import logging
import os
import warnings

# Suppress Google GenAI deprecation warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
warnings.filterwarnings("ignore", category=UserWarning, module="google.generativeai")

import operator  # noqa: E402
import threading  # noqa: E402

import google.generativeai as genai  # noqa: E402
from cachetools import TTLCache, cachedmethod  # noqa: E402
from tenacity import (  # noqa: E402
    before_sleep_log,
    retry,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential,
)

from src.v3.core.schemas import SystemPersonaPayload  # noqa: E402

logger = logging.getLogger(__name__)


class MenirIntel:
    def __init__(self, api_key: str | None = None, ontology=None):
        """
        Inicializa o MenirIntel com suporte a Dual-Boot:
        1. Enterprise (nFADP Compliance): Se VERTEX_PROJECT_ID existir, usa o Google Cloud em Zurique.
        2. Development: Fallback para a API pública do Gemini (genai) usando GOOGLE_API_KEY.

        A Ancoragem da Consciência é feita dinamicamente via `ontology` buscando o nó `(:System:Persona)`.
        Possui cache TTL e fallback físico para evitar SPOF e State Rotting.
        """
        self.ontology = ontology
        self.is_enterprise = False
        self.persona_cache = TTLCache(maxsize=1, ttl=3600)  # 1 hour TTL

        vertex_project = os.getenv("VERTEX_PROJECT_ID")

        if vertex_project:
            logger.info(
                "🛡️ [nFADP Compliance] Explicit Enterprise Configuration Detected. Booting Vertex AI in europe-west6..."
            )
            try:
                import vertexai

                # Force Switzerland/Europe location for Data Residency
                vertexai.init(project=vertex_project, location="europe-west6")
                self.is_enterprise = True
                logger.info("✅ Vertex AI Enterprise Endpoint connected.")
            except ImportError:
                raise ImportError("A biblioteca 'google-cloud-aiplatform' não está instalada.")  # noqa: B904
        else:
            if not api_key:
                api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "Nenhum VERTEX_PROJECT_ID ou GOOGLE_API_KEY fornecido. Initialization failed."
                )

            logger.warning("⚠️ [Development Mode] Inicializando Gemini API Pública.")
            genai.configure(api_key=api_key)

        # Test bootstrapping the persona
        self._get_active_model()

        # V3 Spec: Allowlist (Advanced Ontology)
        self.ALLOWED_LABELS = {
            "Person",
            "Organization",
            "Location",
            "Role",
            "DocumentConcept",
            "Asset",
            "Event",
            "Obligation",
            "Risk",
            "Concept",
            "Year",
            "Month",
            "Day",
        }

        import asyncio

        # Separation of Concerns: Independent Semaphore for parallel LLM Extraction
        # Prevents crashing the Core Watchdog Event Loop during mass 50+ extract bursts
        self.intel_semaphore = asyncio.Semaphore(50)

    @retry(
        stop=(stop_after_attempt(3) | stop_after_delay(60)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def generate_embedding(self, text: str) -> list[float] | None:
        """
        Generates 768-dim vector using Gemini text-embedding-004.
        """
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document",  # Optimized for storage
                request_options={"timeout": 60.0},
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Embedding Gen Error: {e}")
            return None

    @cachedmethod(cache=operator.attrgetter("persona_cache"))
    def _fetch_system_persona(self) -> str:
        """
        Fetches the System Prompt from Neo4j with TTL Cache (1h) to prevent I/O pool exhaustion.
        Applies Pydantic strict validation and asynchronously writes back to local fallback.
        """
        fallback_path = os.path.join(os.getcwd(), "fallback_persona.json")

        if self.ontology:
            try:
                with self.ontology.driver.session(database=self.ontology.db_name) as session:
                    res = session.run(
                        "MATCH (p:System:Persona {name: 'DEFAULT_MENIR'}) RETURN p.name AS name, p.version AS version, p.system_prompt AS system_prompt"
                    ).single()
                    if res:
                        # 1. Pydantic Runtime Validation
                        payload = SystemPersonaPayload(
                            name=res["name"],
                            version=res["version"],
                            system_prompt=res["system_prompt"],
                        )
                        logger.info(
                            f"🧠 [Metacognição] Persona carregada do Grafo e Validada (v{payload.version})."
                        )

                        # 2. Async Write-Back (Mitigate Fallback State Rot)
                        def write_fallback_sync():
                            try:
                                with open(fallback_path, "w", encoding="utf-8") as f:
                                    f.write(payload.model_dump_json(indent=4))
                            except Exception as wf_e:
                                logger.error(f"Failed to write fallback persona: {wf_e}")

                        threading.Thread(target=write_fallback_sync, daemon=True).start()
                        return payload.system_prompt
            except Exception as e:
                logger.error(
                    f"❌ Falha ao buscar Persona do Grafo (Timeout/Validation Error): {e}. Iniciando Fallback local."
                )

        # 3. Boot-Time Fallback
        try:
            with open(fallback_path, encoding="utf-8") as f:
                data = json.load(f)
                payload = SystemPersonaPayload(**data)
                logger.warning(
                    f"⚠️ [Emergency Fallback] Usando Persona local sincronizada pela última vez no Grafo (v{payload.version})."
                )
                return payload.system_prompt
        except Exception as e:
            logger.critical(f"🔥 FALLBACK CORROMPIDO OU INEXISTENTE: {e}")
            raise RuntimeError(  # noqa: B904
                "Não foi possível carregar a Persona do Grafo nem do Fallback local."
            )

    def _get_active_model(self):
        """Builds and returns the GenerativeModel instance using the cached System Persona."""
        persona_prompt = self._fetch_system_persona()
        if self.is_enterprise:
            from vertexai.generative_models import GenerativeModel

            # Vertex AI expects a list for system_instruction
            return GenerativeModel("gemini-1.5-pro-001", system_instruction=[persona_prompt])
        else:
            return genai.GenerativeModel("gemini-2.5-flash", system_instruction=persona_prompt)

    @retry(
        stop=(stop_after_attempt(3) | stop_after_delay(60)),
        wait=wait_exponential(multiplier=2, min=4, max=15),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def structured_inference(
        self,
        prompt: str,
        image_path: str | None = None,
        response_schema=None,
        few_shot_examples: list[dict] | None = None,
    ):
        """
        Inferência Bimodal Unificada e Agnóstica baseada em Schema Pydantic.
        Substitui a antiga ontologia fixa BFO/SKOS, servindo a qualquer Skill de Extração nativamente.
        Pode ser dinamicamente 'ancorada' com Semantic Few-Shot Examples.
        """
        import asyncio
        from typing import Any
        contents: list[Any] = []

        # Semantic Few-Shot Formatting
        if few_shot_examples:
            logger.info(f"⚓ Injecting {len(few_shot_examples)} GoldenExamples into context.")
            system_prompt = "SYSTEM INSTRUCTION: You must strictly replicate the format and structure of the following extraction examples.\n\n"
            for idx, ex in enumerate(few_shot_examples):
                system_prompt += f"--- EXAMPLE {idx + 1} ---\n[INPUT ORIGINAL]\n{ex.get('input_text')}\n\n[OUTPUT ESPERADO]\n{ex.get('ideal_json')}\n\n"
            system_prompt += f"--- FIM DOS EXEMPLOS ---\n\n### TAREFA ATUAL ###\n{prompt}"
            contents.append(system_prompt)
        else:
            contents.append(prompt)

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
            contents[0] += (
                f"\n\nInstrução Mandatória: Retorne APENAS um JSON válido que obedeça ESTRITAMENTE a este Schema. O output tem de ser nativo, cru, e exato:\n{json.dumps(schema_json, ensure_ascii=False)}"
            )

        generation_config = {"response_mime_type": "application/json"}

        try:
            # Separating IO Watchdog from Inference: Wrapped in the Intel Semaphore
            active_model = self._get_active_model()
            async with self.intel_semaphore:
                # Wraps inference in I/O Thread to prevent Event Loop blocking
                response = await asyncio.to_thread(
                    active_model.generate_content, contents, generation_config=generation_config
                )

            raw_text = response.text

            # Clean markdown formatting if the API ignores response_mime_type.
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
            logger.error(
                f"AI Structured Inference Parsing Failed (JSON format error): {j_err} | Text: {raw_text}"
            )
            raise ValueError(f"O modelo injetou quebra de formatação: {j_err}")  # noqa: B904
        except Exception as e:
            logger.error(f"AI Structured Inference Final Execution Failed: {e}")
            raise
