"""
Configuration module for Ganesha Voice Chatbot
"""
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Server Configuration
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Model Configuration
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "google/gemini-2.0-flash-exp:free")
    TTS_LANG_DEFAULT: str = os.getenv("TTS_LANG_DEFAULT", "en")
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "outputs")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50000000"))
    
    # Audio Configuration
    SAMPLE_RATE: int = int(os.getenv("SAMPLE_RATE", "16000"))
    AUDIO_FORMAT: str = os.getenv("AUDIO_FORMAT", "wav")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ]
    
    # Language Support
    SUPPORTED_LANGUAGES = {
        "hi": "Hindi",
        "en": "English", 
        "ta": "Tamil",
        "te": "Telugu",
        "kn": "Kannada",
        "ml": "Malayalam",
        "bn": "Bengali",
        "mr": "Marathi",
        "gu": "Gujarati",
        "pa": "Punjabi",
        "or": "Odia",
        "as": "Assamese",
        "ur": "Urdu"
    }

settings = Settings()
