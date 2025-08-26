# G.O.A.T Bot – Ganapathi Of All Time

A Divine Dialogue with Lord Ganesha, Powered by AI  
Submission for the Ganesh Chaturthi Challenge

## This project is a fully interactive, multilingual voice chatbot that provides a sacred space for users to share their worries and receive wisdom from an AI embodiment of Lord Ganesha. It bridges ancient philosophy with modern technology to create a spiritually uplifting and technically impressive experience.

## Key Features

- **Advanced Voice Input (Speech-to-Text):** Uses faster-whisper for high-accuracy, real-time transcription of user's spoken worries in multiple languages.
- **Philosophical AI Core (LLM):** Powered by the Gemini API, the chatbot generates wise and comforting responses rooted in Ganesha's philosophies and stories.
- **Divine Voice Output (Text-to-Speech):** Uses Edge TTS to convert generated text into a warm, Ganesha-style voice.
- **Multilingual Mastery:** Supports 11+ Indian languages for both voice input and audio output.
- **Animated Ganesha Avatar:** Responsive, animated Ganesha avatar appears when audio response is played.
- **Content Safety:** All responses are spiritually uplifting and free of offensive, political, or disrespectful content.

---

## System Architecture & Workflow

The application uses a modern, decoupled architecture with a Next.js frontend and a Python FastAPI backend.

**Workflow Diagram:**

```
[User]
   |
   v
[Next.js Frontend (Text/Voice Input)]
   |
   v
[API Request to FastAPI Backend]
   |
   v
[Session Manager] -- manages chat sessions and user context
   |
   v
[ASR Service (faster-whisper)] -- transcribes voice input to text (if audio)
   |
   v
[Language Detection & Transliteration] -- detects language, transliterates if needed
   |
   v
[LLM Service (Gemini API)] -- generates philosophical, Ganesha-inspired response
   |
   v
[TTS Service (Edge TTS)] -- converts text response to divine voice audio
   |
   v
[Audio Processing (pydub, ffmpeg)] -- normalizes and enhances audio output
   |
   v
[Response Packager] -- bundles text, audio URL, and metadata
   |
   v
[Next.js Frontend]
   |
   +--> Displays animated Ganesha avatar, shows text, plays audio
```

- **User Interaction:** User speaks or types into the Next.js frontend.
- **API Request:** Frontend sends audio/text data to the Python FastAPI backend.
- **ASR Service:** If audio is received, faster-whisper transcribes it into text.
- **LLM Service:** Transcribed text is sent to Gemini API for a philosophical, Ganesha-inspired response.
- **TTS Service:** Text response is converted into divine voice using Edge TTS.
- **Response to Frontend:** API sends text and audio URL back to the frontend.
- **Final Experience:** User reads the response, sees the Ganesha animation, and hears the audio blessing.

---

## Tech Stack

| Category         | Technology / Library                                              |
| ---------------- | ----------------------------------------------------------------- |
| Frontend         | Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, lucide-react |
| Backend          | Python, FastAPI                                                   |
| Speech-to-Text   | faster-whisper (tiny model for performance)                       |
| LLM              | Google Gemini API                                                 |
| Text-to-Speech   | Edge TTS                                                          |
| Audio Processing | pydub, ffmpeg                                                     |

---

## Configuration & Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YashvanthSankar/ganesh-chaturthi-chatbot.git
cd ganesh-chaturthi-chatbot
```

### 2. Configure Environment Variables

#### Frontend (`frontend/.env.local`)

```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

Set this to your backend URL in production.

#### Backend (`backend/.env`)

```
FRONTEND_URL=http://localhost:3000
GEMINI_API_KEY=your-google-gemini-api-key
# ...other variables as needed
```

Set `FRONTEND_URL` to your deployed frontend URL in production.

### 3. Install Dependencies

#### Frontend

```bash
cd frontend
npm install
```

#### Backend

```bash
cd backend
pip install -r requirements.txt
```

### 4. Run Locally

#### Backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Deployment

- Push your code to a GitHub repository.
- Deploy your frontend and backend to your chosen cloud platform.
- Update environment variables for your deployed domains.
- Ensure ffmpeg is installed on your backend server.

---

Made with devotion by Yashvanth
