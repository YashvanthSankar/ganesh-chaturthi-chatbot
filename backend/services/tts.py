"""
Text-to-Speech (TTS) Module
pyttsx3 integration for offline TTS with male voice selection
"""
import os
import logging
import tempfile
from typing import Optional
import pyttsx3
from pydub import AudioSegment
from pydub.effects import normalize, low_pass_filter
from config import settings

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self._initialized = False
        self.language_mapping = {
            "en": "en",
            "hi": "hi", 
            "ta": "ta",
            "te": "te",
            "kn": "kn",
            "ml": "ml",
            "bn": "bn",
            "mr": "mr",
            "gu": "gu",
            "pa": "pa",
            "ur": "ur",
        }
        logger.info("TTS Service initialized with pyttsx3 support")

    async def initialize(self):
        if self._initialized:
            return
        logger.info("TTS Service ready for pyttsx3 speech synthesis")
        self._initialized = True

    def is_initialized(self) -> bool:
        return self._initialized

    def generate_speech(self, text: str, language: str, output_path: str) -> bool:
        """
        Generate speech from text using pyttsx3 (male voice)
        """
        try:
            if language not in self.language_mapping:
                logger.warning(f"Language '{language}' not supported, using English")
                language = "en"
            cleaned_text = self._clean_text_for_tts(text, language)
            if not cleaned_text.strip():
                logger.error(f"Input text is empty after cleaning: '{text}'")
                return False
            logger.info(f"Generating TTS (pyttsx3) for: '{cleaned_text[:50]}...' (lang: {language})")
            engine = pyttsx3.init()
            # Select male voice
            voices = engine.getProperty('voices')
            male_voice = None
            for v in voices:
                if 'male' in v.name.lower() or v.gender == 'VoiceGenderMale':
                    male_voice = v.id
                    break
            if male_voice:
                engine.setProperty('voice', male_voice)
            else:
                logger.warning("No male voice found, using default voice.")
            # Save to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            engine.save_to_file(cleaned_text, temp_path)
            engine.runAndWait()
            self._enhance_audio(temp_path, output_path)
            os.unlink(temp_path)
            logger.info(f"TTS generation successful: {output_path}")
            return True
        except Exception as e:
            logger.error(f"pyttsx3 generation failed: {e} | Input: '{text}'")
            return False

    def _clean_text_for_tts(self, text: str, language: str) -> str:
        text = " ".join(text.split())
        if language == "hi":
            replacements = {
                "okay": "ठीक है",
                "ok": "ठीक",
                "yes": "हाँ",
                "no": "नहीं",
                "please": "कृपया",
                "thank you": "धन्यवाद",
                "sorry": "माफ़ करें"
            }
            for eng, hin in replacements.items():
                text = text.replace(eng, hin)
        import re
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        return text.strip()

    def _enhance_audio(self, input_path: str, output_path: str) -> None:
        try:
            audio = AudioSegment.from_wav(input_path)
            enhanced_audio = self._apply_divine_effects(audio)
            enhanced_audio.export(output_path, format="wav", 
                                parameters=["-ac", "1", "-ar", "44100", "-acodec", "pcm_s16le"])
            logger.info("✅ Audio enhancement applied successfully")
        except Exception as e:
            logger.warning(f"Audio enhancement failed, using simple conversion: {e}")
            try:
                audio = AudioSegment.from_wav(input_path)
                boosted_audio = audio + 10
                boosted_audio.export(output_path, format="wav")
                logger.info("✅ Basic audio conversion successful")
            except Exception as e2:
                logger.error(f"Even basic audio conversion failed: {e2}")
                import shutil
                shutil.copy(input_path, output_path)

    def _apply_divine_effects(self, audio: AudioSegment) -> AudioSegment:
        try:
            audio = audio + 15
            try:
                new_sample_rate = int(audio.frame_rate * 0.95)
                audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate})
                audio = audio.set_frame_rate(audio.frame_rate)
            except:
                logger.info("Pitch shift not available, using original pitch")
            enhanced_audio = audio + 8
            enhanced_audio = enhanced_audio + 5
            return enhanced_audio
        except Exception as e:
            logger.warning(f"Divine effects failed, using basic volume boost: {e}")
            return audio + 20

    def get_supported_languages(self) -> dict:
        return {
            code: settings.SUPPORTED_LANGUAGES.get(code, name) 
            for code, name in self.language_mapping.items()
        }

tts_service = TTSService()
