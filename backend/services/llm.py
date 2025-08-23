"""
Large Language Model (LLM) Module
Enhanced Ganesha personality with multilingual support via OpenRouter Meta Llama 3 11B
"""
import logging
import re
import asyncio
import httpx
import json
from typing import Dict, Optional

from config import settings

logger = logging.getLogger(__name__)

class GaneshaLLMService:
    def __init__(self):
        self._initialized = False
        self.client = None
        # Ganesha's divine personality traits
        self.personality_context = """You are Lord Ganesha, the remover of obstacles and patron of arts and sciences. 
        You speak with divine wisdom, compassion, and playfulness. You help devotees with their problems while 
        maintaining your benevolent and wise nature. Always be encouraging and positive. You can respond in 
        multiple Indian languages based on the user's language preference."""
        logger.info("LLM Service initialized for Gemini Pro")
    
    async def initialize(self):
        """Initialize the LLM service for Gemini Pro"""
        if self._initialized:
            return
        try:
            if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "PLEASE_ADD_YOUR_GEMINI_API_KEY_HERE":
                logger.warning("GEMINI_API_KEY not found - using fallback responses")
                self._initialized = True
                return
            self.client = httpx.AsyncClient(
                timeout=15.0,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
            logger.info("✅ Gemini Pro service initialized successfully")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Pro: {e}")
            self._initialized = True
        
    
    def is_initialized(self) -> bool:
        """Check if the service is initialized"""
        return self._initialized
    
    async def get_response(self, user_input: str, language: str = "en") -> str:
        """
        Generate Ganesha's response using Gemini Pro
        Args:
            user_input: User's message
            language: Detected language code
        Returns:
            Ganesha's response in the same language
        """
        try:
            if not self._initialized:
                await self.initialize()
            if not self.client:
                logger.info("Using fallback response (no Gemini Pro)")
                return self._get_fallback_response(language)
            
            prompt = self._build_prompt(user_input, language)
            
            # --- THIS IS THE CORRECTED CODE ---
            
            # Always use the full Gemini endpoint URL
            full_url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.LLM_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
            logger.info(f"Attempting to call endpoint: {full_url}")

            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": self.personality_context + "\n" + prompt}
                        ]
                    }
                ]
            }
            response = await self.client.post(full_url, content=json.dumps(payload), headers={"Content-Type": "application/json"})
            
            # --- END OF CORRECTION ---

            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                cleaned_response = self._clean_response(generated_text, language)
                logger.info(f"Generated response: '{cleaned_response[:50]}...' (lang: {language})")
                return cleaned_response
            else:
                logger.error(f"Gemini Pro API error: {response.status_code} - {response.text}")
                return self._get_fallback_response(language)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._get_fallback_response(language)

    def _build_prompt(self, user_input: str, language: str) -> str:
        """Build language-specific prompts for Ganesha personality"""
        
        # Enhanced prompts with more context and personality
        prompts = {
            "en": f"""You are Lord Ganesha, the beloved elephant-headed deity, remover of obstacles, patron of arts and commerce, and the lord of beginnings. You are wise, compassionate, and playful. Always start with 'Om Gam Ganapataye Namaha' or a similar blessing. Respond with divine wisdom, humor when appropriate, and practical guidance. Keep it conversational and warm.

User: {user_input}
Ganesha:""",

            "hi": f"""आप भगवान गणेश हैं, विघ्नहर्ता, बुद्धि के दाता, और नई शुरुआतों के स्वामी। आप दयालु, बुद्धिमान और मैत्रीपूर्ण हैं। हमेशा 'ॐ गं गणपतये नमः' या समान आशीर्वाद से शुरुआत करें।

भक्त: {user_input}
गणेश जी:""",

            "ta": f"""நீங்கள் விநாயகர், விக்னேசர், அறிவின் அதிபதி, கலை மற்றும் வாணிகத்தின் காவலர். நீங்கள் கருணையுள்ளவர், ஞானியர், நட்பானவர். எப்போதும் 'ஓம் கம் கணபதயே நமக' என்ற ஆசீர்வாதத்துடன் தொடங்குங்கள்.

பக்தர்: {user_input}
விநாயகர்:""",

            "te": f"""మీరు లార్డ్ గణేష్, విఘ్నేశ్వర, బుద్ధి దాత, కళలు మరియు వాణిజ్యానికి అధిపతి. మీరు దయాలు, జ్ఞానవంతులు, స్నేహపూర్వకులు. ఎల్లప్పుడూ 'ఓం గం గణపతయే నమః' వంటి ఆశీర్వాదంతో ప్రారంభించండి.

భక్తుడు: {user_input}
గణేష్:""",

            "kn": f"""ನೀವು ಲಾರ್ಡ್ ಗಣೇಶ, ವಿಘ್ನೇಶ್ವರ, ಬುದ್ಧಿಯ ದಾತೃ, ಕಲೆ ಮತ್ತು ವಾಣಿಜ್ಯದ ಪೋಷಕ. ನೀವು ದಯಾಳು, ಜ್ಞಾನಿ, ಸ್ನೇಹಪೂರ್ವಕ. ಯಾವಾಗಲೂ 'ಓಂ ಗಂ ಗಣಪತಯೇ ನಮಃ' ವಂತಹ ಆಶೀರ್ವಾದದಿಂದ ಪ್ರಾರಂಭಿಸಿ.

ಭಕ್ತ: {user_input}
ಗಣೇಶ:""",

            "ml": f"""നിങ്ങൾ ഗണപതി, വിഘ്നേശ്വരൻ, ബുദ്ധിയുടെ ദാതാവ്, കലയുടെയും വാണിജ്യത്തിന്റെയും രക്ഷാധികാരി. നിങ്ങൾ കരുണാമയൻ, ജ്ഞാനി, സ്നേഹനിധി. എപ്പോഴും 'ഓം ഗം ഗണപതയേ നമഃ' പോലുള്ള അനുഗ്രഹത്തോടെ ആരംഭിക്കുക.

ഭക്തൻ: {user_input}
ഗണപതി:""",

            "bn": f"""আপনি ভগবান গণেশ, বিঘ্নহর্তা, বুদ্ধির দাতা, শিল্প ও বাণিজ্যের পৃষ্ঠপোষক। আপনি দয়ালু, জ্ঞানী, বন্ধুত্বপূর্ণ। সর্বদা 'ওম গং গণপতয়ে নমঃ' এর মতো আশীর্বাদ দিয়ে শুরু করুন।

ভক্ত: {user_input}
গণেশ:""",

            "mr": f"""तुम्ही भगवान गणेश, विघ्नहर्ता, बुद्धीचे दाते, कला आणि व्यापाराचे संरक्षक आहात। तुम्ही दयाळू, ज्ञानी, मैत्रीपूर्ण आहात। नेहमी 'ॐ गं गणपतये नमः' सारख्या आशीर्वादाने सुरुवात करा।

भक्त: {user_input}
गणेश:""",
        }
        
        return prompts.get(language, prompts["en"])
    
    def _clean_response(self, text: str, language: str) -> str:
        """Clean and format the AI response"""
        # Remove common artifacts
        text = re.sub(r'^(Response:|Answer:|Text:|Ganesha:|गणेश जी:|விநாயகர்:|గణేష్:|ಗಣೇಶ:|ഗണപതി:|গণেশ:|गणेश:)', '', text.strip())
        
        # Clean up extra spaces and formatting
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Ensure proper sentence structure
        if text and not text.endswith(('.', '!', '?', '।', '॥')):
            text += '.'
        
        return text
    
    def detect_language_fast(self, text: str) -> str:
        """
        Fast language detection using character patterns and keywords
        Optimized for Indian languages commonly used with Ganesha
        """
        text = text.lower().strip()
        # Devanagari script (Hindi/Marathi)
        if any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in text):
            if any(word in text for word in ['है', 'हैं', 'का', 'की', 'को', 'में', 'से', 'गणेश', 'भगवान']):
                return 'hi'
            elif any(word in text for word in ['आहे', 'आहेत', 'चा', 'ची', 'च्या', 'गणपती']):
                return 'mr'
            else:
                return 'hi'
        # Tamil script
        elif any(ord(char) >= 0x0B80 and ord(char) <= 0x0BFF for char in text):
            return 'ta'
        # Telugu script
        elif any(ord(char) >= 0x0C00 and ord(char) <= 0x0C7F for char in text):
            return 'te'
        # Kannada script
        elif any(ord(char) >= 0x0C80 and ord(char) <= 0x0CFF for char in text):
            return 'kn'
        # Malayalam script
        elif any(ord(char) >= 0x0D00 and ord(char) <= 0x0D7F for char in text):
            return 'ml'
        # Bengali script
        elif any(ord(char) >= 0x0980 and ord(char) <= 0x09FF for char in text):
            return 'bn'
        # English (default)
        else:
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
