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
    
    def _transliterate_if_needed(self, text: str) -> str:
        """
        Attempt to transliterate Latin-script Indian language text to native script, with improved heuristics
        """
        try:
            from indic_transliteration.sanscript import transliterate, SCHEMES
            # Try transliterating to all major Indian scripts
            best_native = text
            max_non_ascii = 0
            for script in ["devanagari", "bengali", "tamil", "telugu", "kannada", "malayalam", "gujarati", "oriya", "punjabi"]:
                native = transliterate(text, "itrans", script)
                non_ascii = sum(ord(c) > 127 for c in native)
                if non_ascii > max_non_ascii:
                    max_non_ascii = non_ascii
                    best_native = native
            # If transliteration produced significant non-ASCII, use it
            if max_non_ascii > 0.2 * len(best_native):
                return best_native
        except Exception:
            pass
        return text
    
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
            final_language = self._enhance_language_detection(transcribed_text, primary_language)

            logger.info(f"Transcription successful: '{transcribed_text[:50]}...' (lang: {final_language})")

            return transcribed_text.strip(), final_language

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise Exception(f"Speech recognition error: {str(e)}")

    def _enhance_language_detection(self, text: str, whisper_lang: str, whisper_probs: Optional[dict] = None, langdetect_probs: Optional[dict] = None) -> str:
        """
        Language detection using Whisper and langdetect, always choosing the language with the highest probability.
        whisper_probs: dict of language -> probability from Whisper (if available)
        langdetect_probs: dict of language -> probability from langdetect (if available)
        """
        try:
            # First, try transliteration if text is in Latin script
            transliterated_text = self._transliterate_if_needed(text)
            text_for_detection = transliterated_text if transliterated_text != text else text

            # Whisper
            best_whisper_lang = None
            if whisper_probs:
                best_whisper_lang = max(whisper_probs.items(), key=lambda x: x[1])[0]
                if best_whisper_lang in settings.SUPPORTED_LANGUAGES:
                    return best_whisper_lang
            elif whisper_lang in settings.SUPPORTED_LANGUAGES:
                return whisper_lang

            # langdetect
            from langdetect import detect, LangDetectException
            best_langdetect_lang = None
            if langdetect_probs:
                best_langdetect_lang = max(langdetect_probs.items(), key=lambda x: x[1])[0]
                if best_langdetect_lang in settings.SUPPORTED_LANGUAGES:
                    return best_langdetect_lang
            else:
                try:
                    langdetect_lang = detect(text_for_detection)
                    if langdetect_lang in settings.SUPPORTED_LANGUAGES:
                        return langdetect_lang
                except Exception:
                    pass

            # Fallback to English
            return 'en'
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            if whisper_lang in settings.SUPPORTED_LANGUAGES:
                return whisper_lang
            return 'en'

# Global ASR service instance
asr_service = ASRService()
