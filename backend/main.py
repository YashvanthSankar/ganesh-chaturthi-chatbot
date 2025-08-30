"""
Lord Ganesha Voice Chatbot - FastAPI Backend (Optimized for Hackathon)
"""
import os
import uuid
import logging
from pathlib import Path
import asyncio
import shutil
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager

from config import settings
from services import asr_service, llm_service, tts_service

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

thread_pool_executor = ThreadPoolExecutor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Lord Ganesha Voice Chatbot...")
    initialization_tasks = [asr_service.initialize(), llm_service.initialize(), tts_service.initialize()]
    await asyncio.gather(*initialization_tasks, return_exceptions=True)
    logger.info("All services initialized!")
    yield
    logger.info("Shutting down Ganesha Voice Chatbot.")
    thread_pool_executor.shutdown(wait=True)

app = FastAPI(title="Lord Ganesha Voice Chatbot", version="1.5.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

def save_upload_file_sync(upload_file: UploadFile, destination: Path):
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()

async def run_in_thread_pool(func, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(thread_pool_executor, func, *args)

@app.get("/", summary="Root endpoint with basic info")
async def root():
    return {"message": "Welcome to the Lord Ganesha Voice Chatbot API"}

@app.get("/health", summary="Health check for all services")
async def health_check():
    asr_status, llm_status, tts_status = asr_service.is_initialized(), llm_service.is_initialized(), tts_service.is_initialized()
    healthy = asr_status and llm_status and tts_status
    return JSONResponse(status_code=200 if healthy else 503, content={"status": "healthy" if healthy else "unhealthy", "services": {"asr": "ready" if asr_status else "not ready", "llm": "ready" if llm_status else "not ready", "tts": "ready" if tts_status else "not ready"}})


async def process_chat(user_input: str, input_language_hint: str, session_id: str):
    logger.info(f"Generating Ganesha's response for session {session_id} with language hint '{input_language_hint}'...")
    response_text = await llm_service.get_response(user_input, input_language_hint)
    
    # --- THE CRITICAL FIX IS HERE ---
    # Detect the language of the *actual response* from the LLM.
    # This is the most reliable way to determine the correct voice for TTS.
    response_language = llm_service.detect_language_fast(response_text)
    
    logger.info(f"Ganesha responds (Detected: {response_language}): {response_text}")
    
    logger.info("🎵 Converting text to divine speech...")
    audio_filename = f"{session_id}_response.mp3"
    audio_output_path = OUTPUT_DIR / audio_filename
    
    tts_success = await tts_service.generate_speech(response_text, response_language, str(audio_output_path))
    
    return response_text, response_language, f"/outputs/{audio_filename}" if tts_success else None

@app.post("/chat", summary="Handle voice-based chat")
async def voice_chat(audio: UploadFile = File(...)):
    if not audio.content_type or not audio.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="Invalid file type.")
    
    session_id = str(uuid.uuid4())
    logger.info(f"New voice chat session: {session_id}")
    
    file_extension = Path(audio.filename).suffix or ".webm"
    audio_path = UPLOAD_DIR / f"{session_id}_recording{file_extension}"
    
    await run_in_thread_pool(save_upload_file_sync, audio, audio_path)
    logger.info(f"Saved audio to {audio_path}")
    
    logger.info("Converting speech to text (offloaded to thread pool)...")
    transcription_result = await run_in_thread_pool(asr_service.transcribe_audio, str(audio_path))
    
    if transcription_result is None:
        raise HTTPException(status_code=400, detail="Could not understand the audio. No speech detected.")
        
    user_text, detected_language = transcription_result
    logger.info(f"Transcribed ({detected_language}): {user_text}")
    
    response_text, response_language, audio_url = await process_chat(user_text, detected_language, session_id)
    
    return {"session_id": session_id, "transcription": user_text, "user_message": user_text, "language": detected_language, "response": response_text, "response_language": response_language, "audio_url": audio_url}

@app.post("/text-chat", summary="Handle text-based chat")
async def text_chat(text: str = Form(...)):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")
    
    session_id = str(uuid.uuid4())
    logger.info(f"New text chat session: {session_id}")
    
    detected_language = llm_service.detect_language_fast(text)
    logger.info(f"User message (Detected hint: {detected_language}): '{text}'")
    
    response_text, response_language, audio_url = await process_chat(text, detected_language, session_id)

    return {"session_id": session_id, "user_message": text, "language": detected_language, "response": response_text, "response_language": response_language, "audio_url": audio_url}

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
