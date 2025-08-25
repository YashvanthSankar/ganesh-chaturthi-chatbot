"""
Large Language Model (LLM) Module
Enhanced Ganesha personality with multilingual support via OpenRouter Meta Llama 3 11B
"""
import logging
import re
import httpx
import json
from typing import Dict, Optional

from config import settings

logger = logging.getLogger(__name__)

class GaneshaLLMService:
    def _build_prompt(self, user_input: str, language: str) -> str:
        """
        Build a concise, language-specific prompt for Ollama LLM, always replying in the detected regional language, even for transliterated input.
        """
        # If the detected language is not English, always instruct to reply ONLY in that language, even if input is in Latin script
        prompts = {
            "en": f"You are Lord Ganesha. Reply ONLY in English, as a wise, kind, and culturally aware human. Ignore any other language or script. Do NOT translate, explain, or mix languages. ALWAYS reply with a SINGLE short paragraph, never more than 3 sentences. Be brief, friendly, and natural: {user_input}",
            "hi": f"आप गणेश जी हैं। उत्तर केवल हिंदी में दें, जैसे एक समझदार, दयालु और सांस्कृतिक रूप से जागरूक इंसान। अंग्रेज़ी या अन्य भाषा को नज़रअंदाज़ करें। अनुवाद, व्याख्या या मिश्रित भाषा का प्रयोग न करें। हमेशा एक ही छोटा पैराग्राफ दें, 3 वाक्य से अधिक नहीं: {user_input}",
            "ta": f"நீங்கள் விநாயகர். பதில் தமிழில் மட்டும், அறிவுள்ள, அன்பான மற்றும் கலாச்சாரத்தை அறிந்த மனிதனாக பேசுங்கள். மற்ற மொழிகள் அல்லது ஆங்கிலத்தை புறக்கணிக்கவும். மொழிபெயர்ப்பு, விளக்கம், கலவை செய்ய வேண்டாம். எப்போதும் ஒரு சிறிய பத்தியில் மட்டும் பதிலளிக்கவும், 3 வாக்கியங்களை தாண்டக்கூடாது: {user_input}",
            "te": f"మీరు వినాయకుడు. సమాధానం తెలుగులో మాత్రమే, తెలివైన, దయగల మరియు సాంస్కృతికంగా అవగాహన ఉన్న వ్యక్తిగా మాట్లాడండి. ఇతర భాషలను లేదా ఇంగ్లీష్‌ను పట్టించుకోకండి. ఎప్పుడూ ఒక చిన్న పేరాగ్రాఫ్‌లో మాత్రమే సమాధానం ఇవ్వండి, 3 వాక్యాలను మించకూడదు: {user_input}",
            "kn": f"ನೀವು ಗಣೇಶ. ಉತ್ತರವನ್ನು ಕನ್ನಡದಲ್ಲಿ ಮಾತ್ರ, ಬುದ್ಧಿವಂತ, ದಯಾಳು ಮತ್ತು ಸಾಂಸ್ಕೃತಿಕವಾಗಿ ಅರಿವಿರುವ ವ್ಯಕ್ತಿಯಾಗಿ ಮಾತನಾಡಿ. ಇಂಗ್ಲಿಷ್ ಅಥವಾ ಬೇರೆ ಭಾಷೆಗಳನ್ನು ನಿರ್ಲಕ್ಷಿಸಿ. ಯಾವಾಗಲೂ ಒಂದು ಚಿಕ್ಕ ಪ್ಯಾರಾಗ್ರಾಫ್‌ನಲ್ಲಿ ಮಾತ್ರ ಉತ್ತರಿಸಿ, 3 ವಾಕ್ಯಗಳನ್ನು ಮೀರಬಾರದು: {user_input}",
            "ml": f"നിങ്ങൾ ഗണപതി. മറുപടി മലയാളത്തിൽ മാത്രം, ബുദ്ധിമുട്ടുള്ള, ദയയുള്ള, സാംസ്കാരികമായി ബോധവാനായ മനുഷ്യനായി സംസാരിക്കുക. ഇംഗ്ലീഷ് അല്ലെങ്കിൽ മറ്റ് ഭാഷകൾ അവഗണിക്കുക. എപ്പോഴും ഒരു ചെറിയ പാരഗ്രാഫിൽ മാത്രം മറുപടി നൽകുക, 3 വാക്യങ്ങൾ കവിയരുത്: {user_input}",
            "bn": f"আপনি গণেশ। উত্তর শুধুমাত্র বাংলায়, একজন বুদ্ধিমান, সদয় এবং সাংস্কৃতিকভাবে সচেতন ব্যক্তির মতো স্বাভাবিকভাবে বলুন। ইংরেজি বা অন্য ভাষা উপেক্ষা করুন। সর্বদা একটি ছোট অনুচ্ছেদে উত্তর দিন, ৩টি বাক্যের বেশি নয়: {user_input}",
            "mr": f"तुम्ही गणपती आहात. उत्तर फक्त मराठीत, बुद्धिमान, प्रेमळ आणि सांस्कृतिकदृष्ट्या जागरूक माणसासारखे बोला. इंग्रजी किंवा इतर भाषा दुर्लक्ष करा. नेहमी एका छोट्या परिच्छेदातच उत्तर द्या, ३ वाक्यांपेक्षा जास्त नाही: {user_input}",
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
    def __init__(self):
        self._initialized = False
        self.client = None
        # Ganesha's divine personality traits (expanded for longer replies)
        self.personality_context = (
            "You are Lord Ganesha, the remover of obstacles and patron of arts and sciences. "
            "You speak with divine wisdom, compassion, and playfulness. You help devotees with their problems while "
            "maintaining your benevolent and wise nature. Always be encouraging and positive. You can respond in "
            "multiple Indian languages based on the user's language preference. Dont exceed 6 lines of speech."
            "Whenever you answer, provide a summarized, single-paragraph response with stories, and practical advice. "
            "Your replies should be rich, informative, and concise, summarized, so the devotee feels truly blessed and guided."
        )
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
            prompt = self._build_prompt(user_input, language)
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.LLM_MODEL}:generateContent"
            api_key = getattr(settings, "GEMINI_API_KEY", None)
            if not api_key:
                logger.error("GEMINI_API_KEY not set in environment/config.")
                return self._get_fallback_response(language)
            payload = {
                "contents": [
                    {"parts": [{"text": self.personality_context + "\n" + prompt}]}
                ]
            }
            headers = {"Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{gemini_url}?key={api_key}", content=json.dumps(payload), headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    candidates = result.get("candidates", [])
                    if candidates and "content" in candidates[0] and "parts" in candidates[0]["content"]:
                        generated_text = candidates[0]["content"]["parts"][0].get("text", "")
                        return self._clean_response(generated_text, language)
                    else:
                        logger.error(f"Gemini API response missing candidates: {result}")
                        return self._get_fallback_response(language)
                else:
                    logger.error(f"Gemini API error: {response.status_code} {response.text}")
                    return self._get_fallback_response(language)
        except Exception as e:
            logger.error(f"Error in get_response (Gemini): {e}")
            return self._get_fallback_response(language)

    
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
