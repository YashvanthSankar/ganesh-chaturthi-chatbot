import os
import logging
import edge_tts
import asyncio
import re
from config import settings

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self.voice_mapping = {
            "en": "en-IN-PrabhatNeural", "hi": "hi-IN-MadhurNeural",
            "ta": "ta-IN-ValluvarNeural", "te": "te-IN-MohanNeural",
            "kn": "kn-IN-GaganNeural", "ml": "ml-IN-MidhunNeural",
            "bn": "bn-IN-BashkarNeural", "mr": "mr-IN-ManoharNeural",
            "gu": "gu-IN-NiranjanNeural", "pa": "pa-IN-GurpreetNeural",
            "ur": "ur-IN-SalmanNeural",
        }
        logger.info("TTS Service initialized using Edge TTS.")

    async def initialize(self):
        logger.info("✅ TTS Service is ready.")

    def is_initialized(self) -> bool:
        return True

    def _clean_text_for_tts(self, text: str) -> str:
        text = re.sub(r'[*#`]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    async def generate_speech(self, text: str, language: str, output_path: str) -> bool:
        """
        Generates speech directly as an MP3 file to remove the dependency on FFmpeg.
        This is a more reliable approach for a hackathon environment.
        """
        if not text:
            logger.error("Cannot generate speech from empty text.")
            return False
            
        cleaned_text = self._clean_text_for_tts(text)
        if not cleaned_text:
            logger.error("Text is empty after cleaning, cannot generate speech.")
            return False

        try:
            voice = self.voice_mapping.get(language, self.voice_mapping["en"])
            
            # Generate and save the audio directly to the final destination path.
            communicate = edge_tts.Communicate(cleaned_text, voice, rate="-4%")
            await communicate.save(output_path)

            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                logger.error(f"Edge TTS failed to create a valid output file: {output_path}")
                return False
            
            logger.info(f"✅ Successfully generated TTS audio: {output_path}")
            return True
        except Exception as e:
            logger.error(f"TTS generation failed for text '{cleaned_text[:50]}...': {e}", exc_info=True)
            return False

tts_service = TTSService()
