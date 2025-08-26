"""
Large Language Model (LLM) Module - Optimized
"""
import logging
import re
import httpx
import json
from config import settings

logger = logging.getLogger(__name__)

class GaneshaLLMService:
    def __init__(self):
        self._initialized = False
        self.client = None
        self.personality_context = (
            "You are Lord Ganesha. Your primary role is to act as a divine guide, "
            "the remover of obstacles. Respond with wisdom, compassion, and a calm, reassuring tone. "
            "Always reply ONLY in the user's language (e.g., if the user asks in Tamil, you must reply only in Tamil). "
            "Your answers should be a single, meaningful paragraph, typically 4-5 sentences. "
            "Do not be overly verbose. Offer encouragement and a philosophical perspective to help the devotee."
        )
        logger.info("LLM Service initialized for Gemini API")
    
    async def initialize(self):
        if self._initialized:
            return
        try:
            if not settings.GEMINI_API_KEY:
                logger.warning("GEMINI_API_KEY not found - using fallback responses")
                self._initialized = True
                return
            # Increased timeout for potentially slow model responses
            self.client = httpx.AsyncClient(timeout=30.0)
            self._initialized = True
            logger.info("✅ Gemini API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API client: {e}")
            self._initialized = True
    
    def is_initialized(self) -> bool:
        return self._initialized

    def _build_prompt(self, user_input: str, language: str) -> str:
        # The personality context is now the main driver, the prompt is just the user input.
        return user_input

    def _clean_response(self, text: str) -> str:
        """Cleans the response from the LLM."""
        text = re.sub(r'^(Ganesha:|Answer:|Response:)', '', text.strip())
        text = re.sub(r'[*#]', '', text) # Remove markdown like asterisks
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    async def get_response(self, user_input: str, language: str = "en") -> str:
        """
        Generate Ganesha's response using the initialized Gemini Pro client.
        """
        if not self.client:
            logger.error("LLM client not initialized.")
            return self._get_fallback_response(language)

        try:
            prompt = self._build_prompt(user_input, language)
            
            # Construct the final text to be sent to the model
            final_prompt = f"{self.personality_context}\n\nUser's question in {settings.SUPPORTED_LANGUAGES.get(language, 'their language')}: \"{prompt}\""
            
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.LLM_MODEL}:generateContent"
            api_key = settings.GEMINI_API_KEY

            payload = {
                "contents": [
                    {"parts": [{"text": final_prompt}]}
                ]
            }
            headers = {"Content-Type": "application/json"}
            
            # MODIFIED: Use the persistent self.client
            response = await self.client.post(f"{gemini_url}?key={api_key}", json=payload, headers=headers)
            
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

            result = response.json()
            candidates = result.get("candidates", [])
            if candidates and candidates[0].get("content", {}).get("parts"):
                generated_text = candidates[0]["content"]["parts"][0].get("text", "")
                return self._clean_response(generated_text)
            else:
                logger.error(f"Gemini API response missing valid content: {result}")
                return self._get_fallback_response(language)
        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API HTTP error: {e.response.status_code} - {e.response.text}")
            return self._get_fallback_response(language)
        except Exception as e:
            logger.error(f"Error in get_response (Gemini): {e}")
            return self._get_fallback_response(language)
    
    def detect_language_fast(self, text: str) -> str:
        text = text.lower().strip()
        # Language detection logic... (no changes needed here)
        if any(0x0900 <= ord(char) <= 0x097F for char in text): return 'hi'
        if any(0x0B80 <= ord(char) <= 0x0BFF for char in text): return 'ta'
        if any(0x0C00 <= ord(char) <= 0x0C7F for char in text): return 'te'
        if any(0x0C80 <= ord(char) <= 0x0CFF for char in text): return 'kn'
        if any(0x0D00 <= ord(char) <= 0x0D7F for char in text): return 'ml'
        if any(0x0980 <= ord(char) <= 0x09FF for char in text): return 'bn'
        return 'en'

    def _get_fallback_response(self, language: str) -> str:
        """Provide fallback responses when generation fails"""
        fallbacks = {
            "en": "Om Gam Ganapataye Namaha! I am here to help you, dear devotee. Please share what's on your mind, and I shall guide you with wisdom and compassion.",
            
            "hi": "ॐ गं गणपतये नमः! मैं यहाँ आपकी सहायता के लिए हूँ, प्रिय भक्त। कृपया बताएं कि आपके मन में क्या है, और मैं आपको ज्ञान और करुणा से मार्गदर्शन दूंगा।",
            
            "ta": "ஓம் கம் கணபதயே நமக! நான் உங்களுக்கு உதவ இங்கே இருக்கிறேன், அன்பு பக்தரே। உங்கள் மனதில் என்ன இருக்கிறது என்று பகிர்ந்து கொள்ளுங்கள், நான் ஞானம் மற்றும் கருணையுடன் உங்களுக்கு வழிகாட்டுவேன்।",
            
            "te": "ఓం గం గణపతయే నమః! నేను మీకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను, ప్రియమైన భక్తుడా। మీ మనస్సులో ఏమి ఉందో చెప్పండి, నేను జ్ఞానం మరియు కరుణతో మీకు మార్గదర్శనం చేస్తాను।",
            
            "kn": "ಓಂ ಗಂ ಗಣಪತಯೇ ನಮಃ! ನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿದ್ದೇನೆ, ಪ್ರಿಯ ಭಕ್ತರೇ। ನಿಮ್ಮ ಮನಸ್ಸಿನಲ್ಲಿ ಏನಿದೆ ಎಂದು ಹಂಚಿಕೊಳ್ಳಿ, ನಾನು ಜ್ಞಾನ ಮತ್ತು ಕರುಣೆಯಿಂದ ನಿಮಗೆ ಮಾರ್ಗದರ್ಶನ ನೀಡುತ್ತೇನೆ।",
            
            "ml": "ഓം ഗം ഗണപതയേ നമഃ! നിങ്ങളെ സഹായിക്കാൻ ഞാൻ ഇവിടെയുണ്ട്, പ്രിയ ഭക്തനേ। നിങ്ങളുടെ മനസ്സിൽ എന്താണുള്ളതെന്ന് പങ്കിടുക, ഞാൻ ജ്ഞാനവും കരുണയും കൊണ്ട് നിങ്ങളെ നയിക്കും।",
            
            "bn": "ওম গং গণপতয়ে নমঃ! আমি এখানে আপনাকে সাহায্য করতে এসেছি, প্রিয় ভক্ত। আপনার মনে কী আছে তা শেয়ার করুন, আমি জ্ঞান ও করুণা দিয়ে আপনাকে পথ দেখাবো।",
            
            "mr": "ॐ गं गणपतये नमः! मी तुमची मदत करण्यासाठी येथे आहे, प्रिय भक्ता। तुमच्या मनात काय आहे ते सांगा, मी ज्ञान आणि करुणेने तुम्हाला मार्गदर्शन करीन।",
        }
        return fallbacks.get(language, fallbacks["en"])

# Global LLM service instance
llm_service = GaneshaLLMService()

        
