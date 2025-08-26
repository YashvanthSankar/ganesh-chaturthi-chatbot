"""
Text-to-Speech (TTS) Module - Optimized
"""
import os
import logging
import edge_tts
import asyncio
import re
from pydub import AudioSegment
from config import settings

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self._initialized = False
        self.voice_mapping = {
            "en": "en-IN-PrabhatNeural", "hi": "hi-IN-MadhurNeural",
            "ta": "ta-IN-ValluvarNeural", "te": "te-IN-MohanNeural",
            "kn": "kn-IN-GaganNeural", "ml": "ml-IN-MidhunNeural",
            "bn": "bn-IN-BashkarNeural", "mr": "mr-IN-ManoharNeural",
            "gu": "gu-IN-NiranjanNeural", "pa": "pa-IN-GurpreetNeural",
            "ur": "ur-IN-SalmanNeural",
        }
        logger.info("TTS Service initialized with Edge TTS support")

    async def initialize(self):
        self._initialized = True
        logger.info("TTS Service ready for Edge TTS speech synthesis")

    def is_initialized(self) -> bool:
        return self._initialized

    def _clean_text_for_tts(self, text: str) -> str:
        text = re.sub(r'[\*]', '', text)
        # Keeps essential punctuation for natural speech
        text = re.sub(r'[^\w\s.,?!-]', '', text)
        return text.strip()

    def _enhance_audio_sync(self, input_path: str, output_path: str):
        """Synchronous audio processing part to be run in a thread."""
        try:
            audio = AudioSegment.from_file(input_path)
            # Increase volume by 6dB, a safe and noticeable boost
            enhanced_audio = audio + 6
            enhanced_audio.export(output_path, format="wav")
            logger.info(f"✅ Audio enhancement applied to {output_path}")
        except Exception as e:
            logger.error(f"Audio enhancement failed for {input_path}: {e}")
            # As a fallback, just copy the original file if conversion fails
            import shutil
            shutil.copy(input_path, output_path)

    async def generate_speech(self, text: str, language: str, output_path: str) -> bool:
        """
        Generate speech asynchronously and process it without blocking.
        """
        try:
            voice = self.voice_mapping.get(language, self.voice_mapping["en"])
            cleaned_text = self._clean_text_for_tts(text)

            if not cleaned_text:
                logger.error("Text is empty after cleaning, cannot generate speech.")
                return False

            # Use a temporary file for the initial TTS output
            temp_output_path = output_path.replace(".wav", ".mp3")

            communicate = edge_tts.Communicate(cleaned_text, voice)
            await communicate.save(temp_output_path)
            
            if not os.path.exists(temp_output_path) or os.path.getsize(temp_output_path) == 0:
                logger.error(f"Edge TTS failed to create output file: {temp_output_path}")
                return False

            logger.info(f"Generated TTS mp3: {temp_output_path}")
            
            # Run the blocking pydub operations in a separate thread
            await asyncio.to_thread(self._enhance_audio_sync, temp_output_path, output_path)

            # Clean up temporary mp3 file
            os.remove(temp_output_path)

            logger.info(f"Successfully created final wav: {output_path}")
            return True
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return False

tts_service = TTSService()