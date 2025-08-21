"""
Text-to-Speech (TTS) Module
Enhanced gTTS with audio processing for divine voice effect
"""
import os
import logging
import tempfile
import subprocess
from typing import Optional
from gtts import gTTS
from pydub import AudioSegment
from pydub.effects import normalize, low_pass_filter

from config import settings

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self._initialized = False
        
        # Enhanced language mapping with Indian accent preferences
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
        
        # TLD mapping for better accent (Indian servers when available)
        self.tld_mapping = {
            "en": "co.in",  # Indian English
            "hi": "co.in",  # Hindi
            "ta": "co.in",  # Tamil
            "te": "co.in",  # Telugu
            "kn": "co.in",  # Kannada
            "ml": "co.in",  # Malayalam
            "bn": "co.in",  # Bengali
            "mr": "co.in",  # Marathi
            "gu": "co.in",  # Gujarati
            "pa": "co.in",  # Punjabi
            "ur": "co.in",  # Urdu
        }
        
        logger.info("TTS Service initialized with enhanced Indian language support")
    
    async def initialize(self):
        """Initialize the TTS service"""
        if self._initialized:
            return
            
        logger.info("TTS Service ready for divine speech synthesis")
        self._initialized = True
    
    def is_initialized(self) -> bool:
        """Check if the service is initialized"""
        return self._initialized
    
    def generate_speech(self, text: str, language: str, output_path: str) -> bool:
        """
        Generate speech from text with divine voice enhancement
        
        Args:
            text: Text to convert to speech
            language: Language code
            output_path: Path to save the audio file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate language support
            if language not in self.language_mapping:
                logger.warning(f"Language '{language}' not supported, using English")
                language = "en"
            
            # Clean text for better TTS
            cleaned_text = self._clean_text_for_tts(text, language)
            
            if not cleaned_text.strip():
                raise ValueError("Empty text after cleaning")
            
            # Generate TTS
            tts_lang = self.language_mapping[language]
            tld = self.tld_mapping.get(language, "com")
            
            logger.info(f"Generating TTS for: '{cleaned_text[:50]}...' (lang: {tts_lang}, tld: {tld})")
            
            # Create gTTS object with optimal settings
            tts = gTTS(
                text=cleaned_text,
                lang=tts_lang,
                slow=False,  # Normal speed for better quality
                tld=tld  # Use Indian TLD for better accent
            )
            
            # Save to temporary file first
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_path = temp_file.name
                tts.save(temp_path)
            
            # Enhance audio for divine voice effect
            self._enhance_audio(temp_path, output_path)
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            logger.info(f"TTS generation successful: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return False
    
    def _clean_text_for_tts(self, text: str, language: str) -> str:
        """Clean text for better TTS pronunciation"""
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Language-specific cleaning
        if language == "hi":
            # Replace common English words with Hindi equivalents for better pronunciation
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
        
        # Remove URLs, emails, and special characters that don't pronounce well
        import re
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        return text.strip()
    
    def _enhance_audio(self, input_path: str, output_path: str) -> None:
        """
        Enhance audio for divine, deeper voice effect using pydub
        Falls back to simple conversion if enhancement fails
        """
        try:
            # Load audio
            audio = AudioSegment.from_mp3(input_path)
            
            # Apply enhancements for divine voice
            enhanced_audio = self._apply_divine_effects(audio)
            
            # Export as WAV for better quality with optimal web settings
            enhanced_audio.export(output_path, format="wav", 
                                parameters=[
                                    "-ac", "1",      # Mono channel
                                    "-ar", "44100",  # High sample rate for quality
                                    "-acodec", "pcm_s16le"  # Standard PCM encoding
                                ])
            
            logger.info("✅ Audio enhancement applied successfully")
            
        except Exception as e:
            logger.warning(f"Audio enhancement failed, using simple conversion: {e}")
            try:
                # Fallback: simple conversion without enhancement
                audio = AudioSegment.from_mp3(input_path)
                # Just apply basic volume boost without other effects
                boosted_audio = audio + 10  # 10dB boost
                boosted_audio.export(output_path, format="wav")
                logger.info("✅ Basic audio conversion successful")
            except Exception as e2:
                logger.error(f"Even basic audio conversion failed: {e2}")
                # Last resort: just copy/rename the MP3 as WAV (browser can handle MP3)
                import shutil
                shutil.copy(input_path, output_path.replace('.wav', '.mp3'))
                # Update output_path to MP3
                os.rename(output_path.replace('.wav', '.mp3'), output_path)
    
    def _apply_divine_effects(self, audio: AudioSegment) -> AudioSegment:
        """
        Apply audio effects to create a divine, deeper voice with better volume
        Simplified version to avoid ffmpeg dependencies
        """
        try:
            # Basic volume boost for better audibility
            audio = audio + 15  # 15dB boost
            
            # Try to apply pitch shift (may fail without ffmpeg)
            try:
                # Slightly lower pitch for deeper voice (divine effect)
                new_sample_rate = int(audio.frame_rate * 0.95)
                audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate})
                audio = audio.set_frame_rate(audio.frame_rate)
            except:
                logger.info("Pitch shift not available, using original pitch")
            
            # Additional volume boost
            enhanced_audio = audio + 8  # Additional 8dB boost
            
            # Final boost
            enhanced_audio = enhanced_audio + 5  # Final 5dB boost
            
            return enhanced_audio
            
        except Exception as e:
            logger.warning(f"Divine effects failed, using basic volume boost: {e}")
            # Fallback to simple volume boost
            return audio + 20  # 20dB boost
    
    def get_supported_languages(self) -> dict:
        """Return supported languages for TTS"""
        return {
            code: settings.SUPPORTED_LANGUAGES.get(code, name) 
            for code, name in self.language_mapping.items()
        }

# Global TTS service instance
tts_service = TTSService()
