"""
Configuration module for Ganesha Voice Chatbot
"""
import os
import json
from typing import List
from pathlib import Path
from dotenv import load_dotenv

# Define the base directory
BASE_DIR = Path(__file__).resolve().parent

# Load the .env file
load_dotenv(dotenv_path=BASE_DIR / ".env")

def _get_cors_origins() -> List[str]:
    """Helper function to parse CORS origins from environment variables."""
    cors_env = os.getenv("CORS_ORIGINS")
    if cors_env:
        try:
            # Try to parse it as a JSON list
            return json.loads(cors_env)
        except json.JSONDecodeError:
            # If it's not JSON, treat it as a comma-separated string
            return [origin.strip() for origin in cors_env.split(',')]
    # Fallback to FRONTEND_URL or localhost
    return [os.getenv("FRONTEND_URL", "http://localhost:3000")]

class Settings:
    # Server Configuration
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Model Configuration
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "tiny") # Changed default to tiny
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-flash-latest")
    
    # Gemini Pro Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = _get_cors_origins()
    
    # Language Support
    SUPPORTED_LANGUAGES = {
        "hi": "Hindi", "en": "English", "ta": "Tamil", "te": "Telugu",
        "kn": "Kannada", "ml": "Malayalam", "bn": "Bengali", "mr": "Marathi",
        "gu": "Gujarati", "pa": "Punjabi", "or": "Odia", "as": "Assamese", "ur": "Urdu"
    }

settings = Settings()