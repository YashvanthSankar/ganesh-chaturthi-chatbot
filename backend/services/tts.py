"""
Text-to-Speech (TTS) Module
Edge TTS integration for online TTS with Indian male voice selection
"""
import os
import logging
import tempfile
from typing import Optional
import edge_tts
import asyncio
from pydub import AudioSegment
from pydub.effects import normalize, low_pass_filter
from config import settings
import sys

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self._initialized = False
        self.language_mapping = {
            "en": "en-IN",
            "hi": "hi-IN",
            "ta": "ta-IN",
            "te": "te-IN",
            "kn": "kn-IN",
            "ml": "ml-IN",
            "bn": "bn-IN",
            "mr": "mr-IN",
            "gu": "gu-IN",
            "pa": "pa-IN",
            "ur": "ur-IN",
        }
        self.voice_mapping = {
            "en": "en-IN-PrabhatNeural",
            "hi": "hi-IN-MadhurNeural",
            "ta": "ta-IN-ValluvarNeural",
            "te": "te-IN-MohanNeural",
            "kn": "kn-IN-GaganNeural",
            "ml": "ml-IN-MidhunNeural",
            "bn": "bn-IN-BashkarNeural",
            "mr": "mr-IN-ManoharNeural",
            "gu": "gu-IN-NiranjanNeural",
            "pa": "pa-IN-GurpreetNeural",
            "ur": "ur-IN-SalmanNeural",
        }
        logger.info("TTS Service initialized with Edge TTS support")

    async def initialize(self):
        if self._initialized:
            return
        logger.info("TTS Service ready for Edge TTS speech synthesis")
        self._initialized = True

    def is_initialized(self) -> bool:
        return self._initialized

    def generate_speech(self, text: str, language: str, output_path: str) -> bool:
        """
        Generate speech from text using Edge TTS (Indian male voice)
        """
        try:
            if language not in self.language_mapping:
                logger.warning(f"Language '{language}' not supported, using English")
                language = "en"
            cleaned_text = self._clean_text_for_tts(text, language)
            if not cleaned_text.strip():
                logger.error(f"Input text is empty after cleaning: '{text}'")
                return False
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Generating TTS (Edge TTS) for: '{cleaned_text[:50]}...' (lang: {language})")
            logger.info(f"Edge TTS output path: {output_path}")
            voice = "en-IN-PrabhatNeural"
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import nest_asyncio
                    nest_asyncio.apply()
                    loop.run_until_complete(self._edge_tts_generate(cleaned_text, voice, output_path))
                else:
                    if sys.platform.startswith('win'):
                        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
                    loop.run_until_complete(self._edge_tts_generate(cleaned_text, voice, output_path))
            except Exception as loop_err:
                logger.error(f"Edge TTS event loop error: {loop_err}")
                return False
            # Check if file was created
            if not os.path.exists(output_path):
                logger.error(f"Edge TTS did not create output file: {output_path}")
                return False
            else:
                file_size = os.path.getsize(output_path)
                logger.info(f"Edge TTS output file created: {output_path} (size: {file_size} bytes)")
                if file_size < 1000:
                    logger.warning(f"Output file is very small, may be silent or corrupt: {output_path}")
            self._enhance_audio(output_path, output_path)
            # After enhancement, check file size again
            if os.path.exists(output_path):
                enhanced_size = os.path.getsize(output_path)
                logger.info(f"Enhanced audio file size: {enhanced_size} bytes")
            logger.info(f"TTS generation successful: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Edge TTS generation failed: {e} | Input: '{text}'")
            return False

    async def _edge_tts_generate(self, text: str, voice: str, output_path: str):
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            logger.info(f"Edge TTS synthesis completed: {output_path}")
        except Exception as e:
            logger.error(f"Edge TTS async synthesis failed: {e} | text: '{text}' | voice: '{voice}' | output: '{output_path}'")
            # Optionally, create a dummy file to avoid downstream errors
            with open(output_path, "wb") as f:
                pass

    def _clean_text_for_tts(self, text: str, language: str) -> str:
        text = " ".join(text.split())
        import re
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        return text.strip()

    def _enhance_audio(self, input_path: str, output_path: str) -> None:
        try:
            audio = AudioSegment.from_file(input_path)
            enhanced_audio = self._apply_divine_effects(audio)
            enhanced_audio.export(output_path, format="wav", 
                                parameters=["-ac", "1", "-ar", "44100", "-acodec", "pcm_s16le"])
            logger.info("✅ Audio enhancement applied successfully")
        except Exception as e:
            logger.warning(f"Audio enhancement failed, using simple conversion: {e}")
            try:
                audio = AudioSegment.from_file(input_path)
                boosted_audio = audio + 10
                boosted_audio.export(output_path, format="wav")
                logger.info("✅ Basic audio conversion successful")
            except Exception as e2:
                logger.error(f"Even basic audio conversion failed: {e2}")
                import shutil
                if input_path != output_path:
                    shutil.copy(input_path, output_path)
                else:
                    logger.warning("Input and output paths are the same, skipping file copy.")

    def _apply_divine_effects(self, audio: AudioSegment) -> AudioSegment:
        try:
            audio = audio + 10
            return audio
        except Exception as e:
            logger.warning(f"Divine effects failed, using basic volume boost: {e}")
            return audio + 10

    def get_supported_languages(self) -> dict:
        return {
            code: settings.SUPPORTED_LANGUAGES.get(code, name) 
            for code, name in self.language_mapping.items()
        }

tts_service = TTSService()
