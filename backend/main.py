"""
Lord Ganesha Voice Chatbot - FastAPI Backend (Optimized)
"""
import os
import uuid
import logging
from pathlib import Path
from typing import Optional
import asyncio # MODIFIED: Import asyncio
import shutil # MODIFIED: Import shutil

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager

from config import settings
from services import asr_service, llm_service, tts_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Lifespan Manager for Startup/Shutdown ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🕉️ Initializing Lord Ganesha Voice Chatbot...")
    try:
        logger.info("Loading ASR service...")
        await asr_service.initialize()
        
        logger.info("Loading LLM service...")
        await llm_service.initialize()
        
        logger.info("Loading TTS service...")
        await tts_service.initialize()
        
        logger.info("✨ All services cached and ready!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services during startup: {e}")
    
    yield
    logger.info("Shutting down Ganesha Voice Chatbot.")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Lord Ganesha Voice Chatbot",
    description="A multilingual AI voice chatbot embodying the wisdom of Lord Ganesha",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# --- MODIFIED: Helper function for non-blocking file save ---
def _save_upload_file(upload_file: UploadFile, destination: Path):
    """Saves an uploaded file to a destination in a blocking manner."""
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()

# --- API Endpoints ---
@app.get("/")
async def root():
    return {
        "message": "🕉️ Welcome to Lord Ganesha Voice Chatbot",
        "supported_languages": list(settings.SUPPORTED_LANGUAGES.keys()),
    }

@app.get("/health")
async def health_check():
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
    }

@app.post("/chat")
async def voice_chat(
    audio: UploadFile = File(..., description="Audio file (webm, mp3, wav, m4a)"),
):
    session_id = str(uuid.uuid4())
    logger.info(f"🎙️ New voice chat session: {session_id}")
    
    try:
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Please upload a valid audio file")
        
        file_extension = audio.filename.split('.')[-1] if '.' in audio.filename else 'webm'
        audio_filename = f"{session_id}_recording.{file_extension}"
        audio_path = UPLOAD_DIR / audio_filename
        
        # MODIFIED: Save file in a non-blocking way
        await asyncio.to_thread(_save_upload_file, audio, audio_path)
        logger.info(f"📁 Saved audio: {audio_path}")
        
        # MODIFIED: Transcribe in a non-blocking way
        logger.info("🎯 Converting speech to text...")
        user_text, detected_language = await asyncio.to_thread(
            asr_service.transcribe_audio, str(audio_path)
        )
        
        if not user_text:
            raise HTTPException(status_code=400, detail="Could not understand the audio.")
        logger.info(f"📝 Transcribed ({detected_language}): {user_text}")
        
        logger.info("🧠 Generating Ganesha's response...")
        response_text = await llm_service.get_response(user_text, detected_language)
        logger.info(f"💭 Ganesha responds ({detected_language}): {response_text}")
        
        logger.info("🎵 Converting text to divine speech...")
        response_audio_filename = f"{session_id}_response.wav"
        audio_output_path = OUTPUT_DIR / response_audio_filename
        
        tts_success = await tts_service.generate_speech(
            response_text, detected_language, str(audio_output_path)
        )
        
        audio_url = f"/outputs/{response_audio_filename}" if tts_success else None
        
        return {
            "session_id": session_id,
            "transcription": user_text,
            "detected_language": detected_language,
            "response": response_text,
            "response_language": detected_language,
            "audio_url": audio_url,
        }
        
    except Exception as e:
        logger.error(f"❌ Voice chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/text-chat")
async def text_chat(
    text: str = Form(..., description="Your question or message"),
):
    session_id = str(uuid.uuid4())
    logger.info(f"💬 New text chat session: {session_id}")
    
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Please provide some text")
        
        detected_language = llm_service.detect_language_fast(text)
        logger.info(f"📝 User message: '{text}' (lang: {detected_language})")
        
        response_text = await llm_service.get_response(text, detected_language)
        logger.info(f"💭 Ganesha responds ({detected_language}): {response_text}")
        
        audio_filename = f"{session_id}_response.wav"
        audio_output_path = OUTPUT_DIR / audio_filename
        
        tts_success = await tts_service.generate_speech(
            response_text, detected_language, str(audio_output_path)
        )
        
        audio_url = f"/outputs/{audio_filename}" if tts_success else None

        return {
            "session_id": session_id,
            "user_message": text,
            "response": response_text,
            "response_language": detected_language,
            "audio_url": audio_url,
        }
        
    except Exception as e:
        logger.error(f"❌ Text chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    
# MODIFIED: Added security check to prevent path traversal attacks
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    audio_path = OUTPUT_DIR / filename
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(audio_path, media_type="audio/wav")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG
    )