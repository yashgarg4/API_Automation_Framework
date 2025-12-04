import google.generativeai as genai
from backend.core.config import get_settings


def get_gemini_model(model_name: str = "gemini-2.5-flash"):
    settings = get_settings()
    api_key = settings.GEMINI_API_KEY

    if not api_key:
        # This message will show if .env/env is really missing
        raise RuntimeError("GEMINI_API_KEY not set in .env or environment")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)
