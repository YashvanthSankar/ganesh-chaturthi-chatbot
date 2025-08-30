import torch
import logging
from typing import Tuple, Optional
from faster_whisper import WhisperModel
from langdetect import detect, DetectorFactory, LangDetectException

from config import settings

DetectorFactory.seed = 0
logger = logging.getLogger(__name__)

class ASRService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        self.model: Optional[WhisperModel] = None
        self._initialized = False
        logger.info(f"ASR Service configured for device: {self.device} with compute_type: {self.compute_type}")

    async def initialize(self):
        if self._initialized:
            return
        logger.info(f"Loading Whisper model '{settings.WHISPER_MODEL}'...")
        try:
            self.model = WhisperModel(
                settings.WHISPER_MODEL,
                device=self.device,
                compute_type=self.compute_type,
                download_root="./models"
            )
            self._initialized = True
            logger.info(f"Whisper model '{settings.WHISPER_MODEL}' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}", exc_info=True)
            raise

    def is_initialized(self) -> bool:
        return self._initialized

    def _overwrite_language_if_urdu(self, text: str, detected_language: str) -> str:
        """
        FIX: Checks for Arabic script characters to reliably identify Urdu,
        overriding Whisper's common confusion with Hindi.
        """
        # The Arabic script has a specific Unicode range.
        arabic_script_range = range(0x0600, 0x06FF + 1)
        for char in text:
            if ord(char) in arabic_script_range:
                if detected_language != 'ur':
                    logger.info(f"Script analysis overrides Whisper's detection. Language is Urdu ('ur').")
                return 'ur'
        return detected_language

    def transcribe_audio(self, audio_path: str) -> Optional[Tuple[str, str]]:
        """
        Transcribes an audio file. This is a blocking, CPU/GPU-bound function.
        It should be called from a separate thread or process to avoid blocking the main app.
        """
        if not self.model:
            logger.error("ASR model is not initialized.")
            return None

        try:
            segments, info = self.model.transcribe(
                audio_path,
                beam_size=1,
                language=None,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            transcribed_text = "".join(segment.text for segment in segments).strip()

            if not transcribed_text:
                logger.warning(f"No speech detected in audio file: {audio_path}")
                return None

            # Start with Whisper's detection
            detected_language = info.language
            
            # Apply our reliable Urdu check
            detected_language = self._overwrite_language_if_urdu(transcribed_text, detected_language)
            
            if detected_language not in settings.SUPPORTED_LANGUAGES:
                try:
                    fallback_lang = detect(transcribed_text)
                    if fallback_lang in settings.SUPPORTED_LANGUAGES:
                        detected_language = fallback_lang
                except LangDetectException:
                    pass # Keep the current detection if langdetect fails

            final_language = detected_language if detected_language in settings.SUPPORTED_LANGUAGES else 'en'
            
            logger.info(f"Transcription successful: '{transcribed_text[:50]}...' (Final Language: {final_language})")
            return transcribed_text, final_language

        except Exception as e:
            logger.error(f"Transcription failed for {audio_path}: {e}", exc_info=True)
            return None

asr_service = ASRService()
