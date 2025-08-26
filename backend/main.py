"""
Lord Ganesha Voice Chatbot - FastAPI Backend
A multilingual voice chatbot that embodies the wisdom and blessings of Lord Ganesha
"""
import os
import uuid
import logging
from pathlib import Path
from typing import Optional
import json

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn


from config import settings
from services import asr_service, llm_service, tts_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Lord Ganesha Voice Chatbot",
    description="A multilingual AI voice chatbot embodying the wisdom of Lord Ganesha",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure app for better performance
app.state.asr_service = None
app.state.llm_service = None
app.state.tts_service = None

# Create necessary directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


# Mount static files
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup for better performance"""
    logger.info("🕉️ Initializing Lord Ganesha Voice Chatbot...")
    
    try:
        # Pre-initialize services and cache them in app state
        logger.info("Loading ASR service...")
        app.state.asr_service = asr_service
        await asr_service.initialize()
        
        # Initialize LLM service  
        logger.info("Loading LLM service...")
        app.state.llm_service = llm_service
        await llm_service.initialize()
        
        # Initialize TTS service
        logger.info("Loading TTS service...")
        app.state.tts_service = tts_service
        await tts_service.initialize()
        
        logger.info("✨ All services cached and ready! Ganesha will respond faster.")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "🕉️ Welcome to Lord Ganesha Voice Chatbot",
        "description": "Ask questions and receive divine wisdom in multiple languages",
    "supported_languages": list(settings.SUPPORTED_LANGUAGES.keys()),
        "endpoints": {
            "chat": "/chat (POST) - Voice chat with audio file",
            "text_chat": "/text-chat (POST) - Text-based chat",
            "health": "/health (GET) - Service health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if all services are initialized
        asr_status = asr_service.is_initialized()
        llm_status = llm_service.is_initialized()
        tts_status = tts_service.is_initialized()
        
        overall_status = asr_status and llm_status and tts_status
        
        return {
            "status": "healthy" if overall_status else "unhealthy",
            "services": {
                "asr": "ready" if asr_status else "not ready",
                "llm": "ready" if llm_status else "not ready", 
                "tts": "ready" if tts_status else "not ready"
            },
            "message": "🕉️ All systems blessed by Ganesha" if overall_status else "⚠️ Some services need attention"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/chat")
async def voice_chat(
    audio: UploadFile = File(..., description="Audio file (webm, mp3, wav, m4a)"),
    language: Optional[str] = Form(None, description="Preferred language (auto-detected if not provided)")
):
    """
    Voice chat endpoint - upload audio and get text + audio response
    """
    session_id = str(uuid.uuid4())
    logger.info(f"🎙️ New voice chat session: {session_id}")
    
    try:
        # Validate audio file
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Please upload a valid audio file")
        
        # Save uploaded audio
        audio_filename = f"{session_id}_recording.{audio.filename.split('.')[-1]}"
        audio_path = UPLOAD_DIR / audio_filename
        
        with open(audio_path, "wb") as f:
            content = await audio.read()
            f.write(content)
        
        logger.info(f"📁 Saved audio: {audio_path}")
        
        # Step 1: Speech-to-Text (ASR)
        logger.info("🎯 Converting speech to text...")
        user_text, detected_language = asr_service.transcribe_audio(str(audio_path))
        
        if not user_text:
            raise HTTPException(status_code=400, detail="Could not understand the audio. Please speak clearly.")
        
        logger.info(f"📝 Transcribed ({detected_language}): {user_text}")
        
        # Step 2: Generate LLM Response
        logger.info("🧠 Generating Ganesha's response...")
        response_text = await llm_service.get_response(user_text, detected_language)
        
        logger.info(f"💭 Ganesha responds ({detected_language}): {response_text}")
        
        # Step 3: Text-to-Speech (TTS)
        logger.info("🎵 Converting text to divine speech...")
        audio_filename = f"{session_id}_response.wav"
        audio_output_path = OUTPUT_DIR / audio_filename
        
        # Pass the full response and detected language to TTS for correct voice
        tts_success = tts_service.generate_speech(
            response_text,
            detected_language,
            str(audio_output_path)
        )
        
        if not tts_success:
            logger.warning("TTS failed, returning text-only response")
            return {
                "session_id": session_id,
                "transcription": user_text,
                "detected_language": detected_language,
                "response": response_text,
                "response_language": detected_language,
                "audio_url": None,
                "message": "🕉️ Ganesha's blessing (text only)"
            }
        
        logger.info(f"🔊 Generated audio: {audio_output_path}")
        
        # Prepare response
        response = {
            "session_id": session_id,
            "transcription": user_text,
            "detected_language": detected_language,
            "response": response_text,
            "response_language": detected_language,
            "audio_url": f"/outputs/{audio_filename}",
            "message": "🕉️ Ganesha's divine blessing received"
        }
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Voice chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/text-chat")
async def text_chat(
    text: str = Form(..., description="Your question or message"),
    language: Optional[str] = Form(None, description="Preferred response language")
):
    """
    Text-only chat endpoint that now returns audio as well.
    """
    session_id = str(uuid.uuid4())
    logger.info(f"💬 New text chat session: {session_id}")
    
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Please provide some text")
        
        detected_language = language or llm_service.detect_language_fast(text)
        logger.info(f"📝 User message: '{text}' (lang: {detected_language})")
        
        # Step 1: Generate LLM Response
        logger.info("🧠 Generating Ganesha's response...")
        response_text = await llm_service.get_response(text, detected_language)
        
        logger.info(f"💭 Ganesha responds ({detected_language}): {response_text}")
        
        # Step 2: Text-to-Speech (TTS)
        logger.info("🎵 Converting text to divine speech...")
        audio_filename = f"{session_id}_response.wav"
        audio_output_path = OUTPUT_DIR / audio_filename
        
        tts_success = await tts_service.generate_speech(
            response_text,
            detected_language,
            str(audio_output_path)
        )
        
        audio_url = f"/outputs/{audio_filename}" if tts_success else None
        if not tts_success:
            logger.warning("TTS failed, returning text-only response for text-chat")

        response = {
            "session_id": session_id,
            "user_message": text,
            "response": response_text,
            "response_language": detected_language,
            "audio_url": audio_url,
            "message": "🕉️ Ganesha's wisdom shared"
        }
        return response
        
    except Exception as e:
        logger.error(f"❌ Text chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """
    Serve audio files
    """
    audio_path = OUTPUT_DIR / filename
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        audio_path,
        media_type="audio/wav",
        filename=filename
    )

@app.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages
    """
    return {
    "supported_languages": settings.SUPPORTED_LANGUAGES,
    "total_count": len(settings.SUPPORTED_LANGUAGES),
        "message": "🌍 Ganesha speaks many languages"
    }

if __name__ == "__main__":
    # Run server using PORT from environment (for deployment)
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )