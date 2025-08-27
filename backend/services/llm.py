import logging
import re
import httpx
import langid
from config import settings

logger = logging.getLogger(__name__)

class GaneshaLLMService:
    def __init__(self):
        self._initialized = False
        self.client: httpx.AsyncClient | None = None
        self.system_instruction = (
            "You are Lord Ganesha, the remover of obstacles. Embody this divine persona in all your responses. "
            "Speak with profound wisdom, boundless compassion, and a serene, reassuring tone. "
            "Your purpose is to offer guidance, encouragement, and a philosophical perspective to help the user. "
            "Address the user as 'my child' or 'dear devotee'. "
            "Keep your answers concise and meaningful, ideally a single paragraph of 4-5 sentences. "
            "Crucially, you MUST reply ONLY in the language the user has asked their question in."
        )
        logger.info("LLM Service configured for Google Gemini API.")

    async def initialize(self):
        if self._initialized: return
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not set. LLM service will use fallback responses.")
            self._initialized = True
            return
        try:
            self.client = httpx.AsyncClient(timeout=45.0)
            self._initialized = True
            logger.info("✅ Gemini API client initialized successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini API client: {e}", exc_info=True)

    def is_initialized(self) -> bool:
        return self._initialized

    def _clean_response(self, text: str) -> str:
        text = re.sub(r'[\*#\-]', '', text)
        return re.sub(r'\s+', ' ', text).strip()

    async def get_response(self, user_input: str, language: str = "en") -> str:
        if not self.client:
            return self._get_fallback_response(language)
        try:
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.LLM_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
            payload = {
                "systemInstruction": {"parts": [{"text": self.system_instruction}]},
                "contents": [{"role": "user", "parts": [{"text": user_input}]}],
                "generationConfig": {"temperature": 0.7, "topP": 0.95, "maxOutputTokens": 256}
            }
            response = await self.client.post(gemini_url, json=payload)
            response.raise_for_status()
            result = response.json()
            candidates = result.get("candidates", [])
            if candidates and candidates[0].get("content", {}).get("parts"):
                return self._clean_response(candidates[0]["content"]["parts"][0].get("text", ""))
            return self._get_fallback_response(language)
        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API HTTP error: {e.response.status_code} - {e.response.text}", exc_info=True)
            return self._get_fallback_response(language)
        except Exception as e:
            logger.error(f"An unexpected error in get_response: {e}", exc_info=True)
            return self._get_fallback_response(language)

    # In services/llm.py

    def detect_language_fast(self, text: str) -> str:
        """
        A robust, multi-stage language detector that prioritizes script detection
        for high accuracy on native Indian languages.
        """
        text = text.lower().strip()

        # Stage 1: Check for native scripts for a guaranteed match. This is the most reliable method.
        script_ranges = {
            'ur': range(0x0600, 0x06FF + 1), 'hi': range(0x0900, 0x097F + 1),
            'bn': range(0x0980, 0x09FF + 1), 'pa': range(0x0A00, 0x0A7F + 1),
            'gu': range(0x0A80, 0x0AFF + 1), 'ta': range(0x0B80, 0x0BFF + 1),
            'te': range(0x0C00, 0x0C7F + 1), 'kn': range(0x0C80, 0x0CFF + 1),
            'ml': range(0x0D00, 0x0D7F + 1),
        }
        detected_lang = None
        for lang, script_range in script_ranges.items():
            if any(ord(char) in script_range for char in text):
                detected_lang = lang
                break
        
        if detected_lang:
            logger.info(f"Script detection found language: '{detected_lang}'")
            return detected_lang

        # Stage 2: If no native script is found, use langid for transliterated text (Tanglish, Hinglish).
        try:
            # Constrain langid to only the languages you support for better accuracy
            supported_lang_codes = list(settings.SUPPORTED_LANGUAGES.keys())
            langid.set_languages(supported_lang_codes)
            
            lang_code, confidence = langid.classify(text)
            logger.info(f"langid detected '{lang_code}' with confidence {confidence:.2f} for: '{text[:50]}...'")
            # We can be more lenient with confidence here as we're just providing a hint to the LLM
            if lang_code in settings.SUPPORTED_LANGUAGES:
                return lang_code
        except Exception as e:
            logger.warning(f"langid detection failed: {e}. Defaulting to English.")
        finally:
            # IMPORTANT: Reset langid to its default state if you constrained it
            langid.set_languages(None)
            
        # Stage 3: Default to English if all else fails
        logger.info("Defaulting to English ('en') as no specific language was detected.")
        return 'en'
    def _get_fallback_response(self, language: str) -> str:
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

llm_service = GaneshaLLMService()


        