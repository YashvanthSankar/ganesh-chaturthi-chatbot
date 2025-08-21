# 🕉️ Lord Ganesha Voice Chatbot

A multilingual AI voice chatbot powered by Lord Ganesha's divine wisdom, featuring advanced voice activity detection, real-time speech processing, and beautiful UI.

## ✨ Features

- **🎤 Voice Activity Detection** - Automatically stops recording when you stop speaking
- **🗣️ Multilingual Support** - Speak in any Indian language or type in English
- **🎵 Divine Voice Synthesis** - Lord Ganesha's blessed voice responses
- **🎨 Beautiful UI** - Professional design with shadcn/ui components
- **⚡ Real-time Processing** - Powered by Gemini 2.0 Flash via OpenRouter
- **🔊 Smart Audio Controls** - Auto-play/stop with visual feedback

## 🛠️ Tech Stack

### Backend
- FastAPI
- faster-whisper
- OpenRouter + Gemini 2.0 Flash
- gTTS + pydub

### Frontend
- Next.js 14
- shadcn/ui
- Tailwind CSS
- Web Audio API

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenRouter API Key

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YashvanthSankar/ganesh-chaturthi-chatbot.git
   cd ganesh-chaturthi-chatbot/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables:**
   ```bash
   # Create .env file
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

5. **Run the backend:**
   ```bash
   python main.py
   ```
   
   The backend will start on `http://localhost:8000`
   
   **Note:** On first run, the Whisper model (~145MB) will be automatically downloaded.

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```
   
   The frontend will start on `http://localhost:3000`

## 🎯 How to Use

1. **Open your browser** to `http://localhost:3000`
2. **Click "Enable Audio"** if prompted (required for voice responses)
3. **Start chatting:**
   - **Text**: Type your message and press Enter
   - **Voice**: Click the microphone button and start speaking
4. **Voice Recording:**
   - Button turns **green** when voice is detected
   - Button turns **red** during silence
   - **Auto-stops** after 2 seconds of silence
   - **Automatically sends** your message

## 🎨 UI Features

### Voice Activity Detection
- **🟢 Green Button** - Voice detected, keep speaking!
- **🔴 Red Button** - Silence detected, will auto-stop soon
- **📊 Real-time Feedback** - Visual indicators for recording status

### Audio Controls
- **🔊 Play/Stop** - Individual message audio controls
- **🔇 Mute/Unmute** - Global audio toggle
- **⏹️ Stop Audio** - Global stop button when audio is playing

### Smart Features
- **Auto-scroll** - Chat automatically scrolls to new messages
- **Word wrapping** - Long messages display properly
- **Responsive design** - Works on all device sizes
- **Dark mode support** - Automatic theme switching

## 🔧 Configuration

### Voice Detection Settings
In `frontend/src/app/page.tsx`:
```typescript
const VOICE_THRESHOLD = 30; // Adjust sensitivity (10-50)
const SILENCE_DURATION = 2000; // Auto-stop delay in ms
```

### Audio Quality Settings
In backend voice services:
- **Sample Rate**: 44.1kHz
- **Echo Cancellation**: Enabled
- **Noise Suppression**: Enabled

## 📂 Project Structure

```
ganesh-chaturthi-chatbot/
├── backend/
│   ├── services/          # AI services (ASR, LLM, TTS)
│   ├── main.py           # FastAPI application
│   ├── requirements.txt  # Python dependencies
│   └── .env             # Environment variables
├── frontend/
│   ├── src/app/         # Next.js app directory
│   ├── components/ui/   # shadcn/ui components
│   ├── package.json     # Node dependencies
│   └── tailwind.config.ts
└── README.md
```

## 🚨 Important Notes

- **Model Files**: Whisper models (~145MB) are automatically downloaded on first run
- **Audio Permissions**: Browser will request microphone access
- **HTTPS**: For production, use HTTPS for microphone access
- **API Limits**: OpenRouter API has usage limits

## 🔒 Environment Variables

Create `.env` file in backend directory:
```env
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
```

## 🆘 Troubleshooting

### Audio Issues
- **No voice responses**: Click "Enable Audio" button
- **Recording not working**: Check microphone permissions
- **Auto-stop not working**: Adjust `VOICE_THRESHOLD` value

### Backend Issues
- **Model not found**: Delete `backend/models/` and restart
- **API errors**: Check your OpenRouter API key
- **Port conflicts**: Change port in `main.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📜 License

This project is open source and available under the MIT License.

## 🙏 Credits

- **Lord Ganesha** - Divine inspiration and guidance
- **OpenRouter** - AI model access
- **shadcn/ui** - Beautiful components
- **FastAPI** - Backend framework
- **Next.js** - Frontend framework

---

**🕉️ Ganpati Bappa Morya! May Lord Ganesha remove all obstacles from your path! 🙏**
