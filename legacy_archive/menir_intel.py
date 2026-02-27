import google.generativeai as genai
import json
import os
import time
import warnings
from dotenv import load_dotenv

load_dotenv(override=True)
warnings.filterwarnings("ignore")

_CACHED_MODELS = None


def _resolve_gemini_api_key():
    gemini_key = os.getenv("GEMINI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        return gemini_key, "GEMINI_API_KEY"
    if google_key:
        return google_key, "GOOGLE_API_KEY"
    return None, None


def _safe_list_generate_models():
    global _CACHED_MODELS
    if _CACHED_MODELS is not None:
        return _CACHED_MODELS
    try:
        models = list(genai.list_models())
        generate_models = []
        for model in models:
            supported = getattr(model, "supported_generation_methods", None) or []
            if "generateContent" in supported:
                generate_models.append(model)
        _CACHED_MODELS = generate_models
        return generate_models
    except Exception:
        _CACHED_MODELS = []
        return _CACHED_MODELS


def _pick_model_name(preferred_name: str):
    # Allow override via env without code changes.
    env_model = (os.getenv("GEMINI_MODEL") or "").strip()
    if env_model:
        return env_model

    # Prefer a stable slug by default.
    preferred_name = (preferred_name or "gemini-1.5-flash").strip()

    # If we can list models, pick a supported one that actually exists.
    models = _safe_list_generate_models()
    if models:
        names = {getattr(m, "name", "") for m in models}
        if preferred_name in names:
            return preferred_name
        if f"models/{preferred_name}" in names:
            return f"models/{preferred_name}"

        # Heuristics: prefer "flash" models, then any Gemini model.
        for m in models:
            name = getattr(m, "name", "")
            if "flash" in name and "gemini" in name:
                return name
        for m in models:
            name = getattr(m, "name", "")
            if "gemini" in name:
                return name

        # Last resort: first generate-capable model.
        return getattr(models[0], "name", preferred_name)

    return preferred_name

def get_menir_prompt():
    return """
    ROLE: Menir Knowledge Engine.
    CONTEXT: User 'Luiz' (Root). Entities: 'LibLabs', 'MAU', 'Tivoli'.
    TASK: Map INPUT to Graph.
    RULES:
    1. Filename "TIVOLI" -> Link to Project 'Tivoli'.
    2. Map "Carol" -> 'Caroline Moreira'.
    OUTPUT JSON: { "nodes": [...], "edges": [...] }
    """

def analyze_document_content(text_content, filename_context="Unknown"):
    api_key, key_source = _resolve_gemini_api_key()
    if not api_key:
        print("❌ [Intel] ERRO: Chave Gemini ausente. Defina GEMINI_API_KEY (ou GOOGLE_API_KEY).")
        return None

    try:
        genai.configure(api_key=api_key)

        model_name = _pick_model_name("gemini-1.5-flash")
        model = genai.GenerativeModel(model_name)
        
        full_prompt = f"""
        {get_menir_prompt()}
        --- INPUT ---
        FILE: {filename_context}
        TEXT: {text_content[:25000]}
        """
        
        response = model.generate_content(
            full_prompt,
            generation_config={"response_mime_type": "application/json"},
        )
        
        if not response.text:
            raise ValueError("IA retornou texto vazio.")
            
        return json.loads(response.text)

    except Exception as e:
        # Don’t leak keys; only provide actionable context.
        model_name = (os.getenv("GEMINI_MODEL") or "gemini-1.5-flash").strip() or "gemini-1.5-flash"
        print(
            "❌ [Intel] ERRO REAL: "
            f"{e} | key={key_source or 'NONE'} | model={model_name} | "
            "dica: defina GEMINI_MODEL com um modelo existente (ListModels)."
        )
        return None
