# G.O.A.T Bot – Ganapathi Of All Time

## Tech Stack

- **Frontend:** Next.js, Tailwind CSS, shadcn/ui
- **Backend:** FastAPI, Python, Gemini API, Edge TTS, pydub, ffmpeg

## Environment Variables

### Frontend (`frontend/.env.local`)

```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

Set to your backend URL in production.

### Backend (`backend/.env`)

```
FRONTEND_URL=http://localhost:3000
DEBUG=True
HOST=0.0.0.0
PORT=8000
NEXT_PUBLIC_API_BASE=http://localhost:8000

WHISPER_MODEL=base
LLM_MODEL=gemini-2.0-flash
TTS_LANG_DEFAULT=en

GEMINI_API_KEY=your-gemini-api-key

UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
MAX_FILE_SIZE=50000000

SAMPLE_RATE=16000
AUDIO_FORMAT=wav

CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

Set `FRONTEND_URL` and `CORS_ORIGINS` to your deployed frontend URL in production.

## How to Run Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Deployment

- Update all URLs in `.env` files for your deployed domains.
- Ensure ffmpeg is installed on your backend server.

---

Made by Yashvanth S
