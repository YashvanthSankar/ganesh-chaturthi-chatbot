"""
Automatic Speech Recognition (ASR) Module
Using faster-whisper for multilingual speech-to-text conversion
"""
import os
import torch
import logging
from typing import Tuple, Optional
from faster_whisper import WhisperModel
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

from config import settings

# Set seed for consistent language detection
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

class ASRService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        self.model = None
        self._initialized = False
        
        logger.info(f"ASR Service initialized for device: {self.device}")
    
    async def initialize(self):
        """Initialize the ASR service by loading the Whisper model"""
        if self._initialized:
            return
            
        logger.info("Loading Whisper model...")
        
        try:
            self.model = WhisperModel(
                settings.WHISPER_MODEL, 
                device=self.device, 
                compute_type=self.compute_type,
                download_root="./models"
            )
            self._initialized = True
            logger.info(f"✅ Whisper model '{settings.WHISPER_MODEL}' loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            raise
    
    def is_initialized(self) -> bool:
        """Check if the service is initialized"""
        return self._initialized
    
    def transcribe_audio(self, audio_path: str) -> Tuple[str, str]:
        """
        Transcribe audio file and detect language
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (transcribed_text, detected_language)
        """
        try:
            # Primary transcription with Whisper
            segments, info = self.model.transcribe(
                audio_path,
                beam_size=5,
                language=None,  # Auto-detect
                task="transcribe",
                vad_filter=True,  # Voice Activity Detection
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                    speech_pad_ms=400
                ),
                word_timestamps=False
            )
            
            # Extract text and language
            primary_language = info.language
            transcribed_text = " ".join([segment.text.strip() for segment in segments])
            
            if not transcribed_text.strip():
                raise ValueError("No speech detected in audio")
            
            # Secondary language detection for Indian languages
            final_language = self._enhance_language_detection(
                transcribed_text, 
                primary_language
            )
            
            logger.info(f"Transcription successful: '{transcribed_text[:50]}...' (lang: {final_language})")
            
            return transcribed_text.strip(), final_language
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise Exception(f"Speech recognition error: {str(e)}")
    
    def _enhance_language_detection(self, text: str, whisper_lang: str) -> str:
        """
        Enhance language detection using multiple methods
        """
        try:
            # Use langdetect as secondary verification
            detected_lang = detect(text)
            
            # Mapping for better Indian language support
            lang_mapping = {
                'hi': 'hi',  # Hindi
                'ta': 'ta',  # Tamil
                'te': 'te',  # Telugu
                'kn': 'kn',  # Kannada
                'ml': 'ml',  # Malayalam
                'bn': 'bn',  # Bengali
                'mr': 'mr',  # Marathi
                'gu': 'gu',  # Gujarati
                'pa': 'pa',  # Punjabi
                'ur': 'ur',  # Urdu
                'en': 'en',  # English
            }
            
            # Prefer Whisper for Indian languages, langdetect for others
            if whisper_lang in settings.SUPPORTED_LANGUAGES:
                final_lang = whisper_lang
            elif detected_lang in lang_mapping:
                final_lang = detected_lang
            else:
                final_lang = whisper_lang if whisper_lang else 'en'
            
            # Ensure we support the language
            if final_lang not in settings.SUPPORTED_LANGUAGES:
                final_lang = 'en'  # Default to English
                
            return final_lang
            
        except LangDetectException:
            # Fallback to Whisper detection
            return whisper_lang if whisper_lang in settings.SUPPORTED_LANGUAGES else 'en'
    
    def get_supported_languages(self) -> dict:
        """Return supported languages"""
        return settings.SUPPORTED_LANGUAGES

# Global ASR service instance
asr_service = ASRService()
