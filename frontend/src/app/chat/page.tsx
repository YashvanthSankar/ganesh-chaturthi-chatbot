'use client';

import React, { useRef, useEffect, useReducer } from 'react';
import { useRouter } from 'next/navigation';
import { Mic, MicOff, Send, Volume2, VolumeX, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

// --- Type Definitions ---
interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  language?: string;
  audioUrl?: string;
  timestamp: Date;
}

interface ChatResponse {
  session_id: string;
  transcription?: string;
  user_message: string;
  response: string;
  language?: string;
  response_language?: string;
  audio_url?: string;
}

// --- State Management with useReducer ---
type State = {
  messages: Message[];
  textInput: string;
  isRecording: boolean;
  isProcessing: boolean;
  isMuted: boolean;
  isPlaying: boolean;
  playingMessageId: string | null;
  isClient: boolean;
  isGaneshaSpeaking: boolean;
  voiceDetected: boolean;
};

type Action =
  | { type: 'SET_MESSAGES'; payload: Message[] }
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'UPDATE_USER_VOICE_MESSAGE'; payload: { id: string; content: string; language?: string } }
  | { type: 'SET_TEXT_INPUT'; payload: string }
  | { type: 'SET_IS_RECORDING'; payload: boolean }
  | { type: 'SET_IS_PROCESSING'; payload: boolean }
  | { type: 'TOGGLE_MUTE' }
  | { type: 'SET_IS_PLAYING'; payload: { isPlaying: boolean; messageId: string | null } }
  | { type: 'SET_IS_CLIENT'; payload: boolean }
  | { type: 'SET_GANESHA_SPEAKING'; payload: boolean }
  | { type: 'SET_VOICE_DETECTED'; payload: boolean };

const initialState: State = {
  messages: [],
  textInput: '',
  isRecording: false,
  isProcessing: false,
  isMuted: false,
  isPlaying: false,
  playingMessageId: null,
  isClient: false,
  isGaneshaSpeaking: false,
  voiceDetected: false,
};

function chatReducer(state: State, action: Action): State {
    switch (action.type) {
        case 'SET_MESSAGES':
          return { ...state, messages: action.payload };
        case 'ADD_MESSAGE':
          return { ...state, messages: [...state.messages, action.payload] };
        case 'UPDATE_USER_VOICE_MESSAGE':
          return {
            ...state,
            messages: state.messages.map((msg) =>
              msg.id === action.payload.id
                ? { ...msg, content: action.payload.content, language: action.payload.language }
                                : msg
            ),
          };
        case 'SET_TEXT_INPUT':
          return { ...state, textInput: action.payload };
        case 'SET_IS_RECORDING':
          return { ...state, isRecording: action.payload };
        case 'SET_IS_PROCESSING':
          return { ...state, isProcessing: action.payload };
        case 'TOGGLE_MUTE':
          return { ...state, isMuted: !state.isMuted, isGaneshaSpeaking: false };
        case 'SET_IS_PLAYING':
          return { ...state, isPlaying: action.payload.isPlaying, playingMessageId: action.payload.messageId };
        case 'SET_IS_CLIENT':
          return { ...state, isClient: action.payload };
        case 'SET_GANESHA_SPEAKING':
          return { ...state, isGaneshaSpeaking: action.payload };
        case 'SET_VOICE_DETECTED':
          return { ...state, voiceDetected: action.payload };
        default:
          return state;
      }
}

export default function ChatPage() {
  const router = useRouter();
  const [state, dispatch] = useReducer(chatReducer, initialState);
  const { messages, textInput, isRecording, isProcessing, isMuted, isPlaying, playingMessageId, isClient, isGaneshaSpeaking, voiceDetected } = state;

  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const videoRefMobile = useRef<HTMLVideoElement | null>(null);
  const videoRefTablet = useRef<HTMLVideoElement | null>(null);
  const videoRefLeft = useRef<HTMLVideoElement | null>(null);
  const videoRefRight = useRef<HTMLVideoElement | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const silenceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null); // FIXED: Changed type from NodeJS.Timeout
  const hasSpokenRef = useRef(false);

  useEffect(() => {
    dispatch({ type: 'SET_IS_CLIENT', payload: true });
    try {
      const stored = window.localStorage.getItem('ganesha_chat_history');
      if (stored) {
        type StoredMessage = Omit<Message, 'timestamp'> & { timestamp: string };
        const parsed: Message[] = (JSON.parse(stored) as StoredMessage[]).map((msg) => ({
          ...msg,
          timestamp: new Date(msg.timestamp), 
        }));
        dispatch({ type: 'SET_MESSAGES', payload: parsed });
      } else {
        const welcomeMessage: Message = {
          id: 'welcome',
          type: 'assistant',
          content: '🕉️ Namaste! I am Lord Ganesha. How may I bless you today? 🙏',
          timestamp: new Date(),
        };
        dispatch({ type: 'SET_MESSAGES', payload: [welcomeMessage] });
      }
    } catch {
      window.localStorage.removeItem('ganesha_chat_history');
      dispatch({ type: 'SET_MESSAGES', payload: [] });
    }
  }, []);

  useEffect(() => {
    if (isClient) {
      window.localStorage.setItem('ganesha_chat_history', JSON.stringify(messages));
    }
  }, [messages, isClient]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    return () => {
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      audioContextRef.current?.close();
    };
  }, []);

  const playAudio = async (url: string, messageId: string) => {
    if (isMuted) return;
    if (audioPlayerRef.current) audioPlayerRef.current.pause();

    const audio = new Audio(url);
    const allVideos = [videoRefMobile.current, videoRefTablet.current, videoRefLeft.current, videoRefRight.current];

    // FIXED: Moved onStop definition inside this function's scope
    const onStop = () => {
        dispatch({ type: 'SET_IS_PLAYING', payload: { isPlaying: false, messageId: null } });
        dispatch({ type: 'SET_GANESHA_SPEAKING', payload: false });
        allVideos.forEach(v => v?.pause());
    };

    audio.onplay = () => {
      dispatch({ type: 'SET_IS_PLAYING', payload: { isPlaying: true, messageId } });
      dispatch({ type: 'SET_GANESHA_SPEAKING', payload: true });
      allVideos.forEach(v => v?.play());
    };
    audio.onended = onStop;
    audio.onpause = onStop;

    try {
      await audio.play();
      audioPlayerRef.current = audio;
    } catch (error) {
      console.error('Audio play failed:', error);
      onStop();
    }
  };

  const stopAudio = () => {
    audioPlayerRef.current?.pause();
  };
  
  const toggleMute = () => {
    dispatch({ type: 'TOGGLE_MUTE' });
    if (!isMuted) stopAudio();
  };

  const sendTextMessage = async () => {
    if (!textInput.trim() || isProcessing) return;
    dispatch({ type: 'SET_IS_PROCESSING', payload: true });
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: textInput,
      timestamp: new Date(),
    };
    dispatch({ type: 'ADD_MESSAGE', payload: userMessage });
    dispatch({ type: 'SET_TEXT_INPUT', payload: '' });
    try {
      const formData = new FormData();
      formData.append('text', userMessage.content);
      const response = await fetch(`${API_BASE}/text-chat`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data: ChatResponse = await response.json();
      const assistantMessage: Message = {
        id: data.session_id,
        type: 'assistant',
        content: data.response,
        timestamp: new Date(),
        language: data.response_language || data.language,
        audioUrl: data.audio_url ? `${API_BASE}${data.audio_url}` : undefined,
      };
      dispatch({ type: 'ADD_MESSAGE', payload: assistantMessage });
      if (assistantMessage.audioUrl) playAudio(assistantMessage.audioUrl, assistantMessage.id);
    } catch (error) {
      console.error('Text chat error:', error);
      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          id: 'error-' + Date.now(),
          type: 'assistant',
          content: 'My apologies, something went wrong. Please try again.',
          timestamp: new Date(),
        },
      });
    } finally {
      dispatch({ type: 'SET_IS_PROCESSING', payload: false });
    }
  };

  const cleanupVAD = () => {
    if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
    audioContextRef.current?.close().catch(() => {});
    audioContextRef.current = null;
    analyserRef.current = null;
    dispatch({ type: 'SET_VOICE_DETECTED', payload: false });
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    dispatch({ type: 'SET_IS_RECORDING', payload: false });
    cleanupVAD();
  };

  const startVoiceActivityDetection = (stream: MediaStream) => {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);
    
    analyser.fftSize = 256;
    analyser.minDecibels = -70;
    source.connect(analyser);

    audioContextRef.current = audioContext;
    analyserRef.current = analyser;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    const silenceDelay = 1000;
    const checkInterval = 200;

    const check = () => {
        if (!analyserRef.current || !mediaRecorderRef.current || mediaRecorderRef.current.state !== 'recording') {
            return;
        }

        analyserRef.current.getByteFrequencyData(dataArray);
        const sum = dataArray.reduce((a, b) => a + b, 0);
        const average = sum / bufferLength;

        if (average > 2) {
            hasSpokenRef.current = true;
            dispatch({ type: 'SET_VOICE_DETECTED', payload: true });
            if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
            silenceTimerRef.current = setTimeout(stopRecording, silenceDelay);
        } else {
            dispatch({ type: 'SET_VOICE_DETECTED', payload: false });
        }

        if (mediaRecorderRef.current.state === 'recording') {
            setTimeout(check, checkInterval);
        }
    };
    check();
  };
  
  const startRecording = async () => {
    if (isRecording) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      dispatch({ type: 'SET_IS_RECORDING', payload: true });
      hasSpokenRef.current = false;

      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      audioChunksRef.current = [];
      mediaRecorderRef.current.ondataavailable = (event) => audioChunksRef.current.push(event.data);
      mediaRecorderRef.current.onstop = () => {
        stream.getTracks().forEach((track) => track.stop());
        if (hasSpokenRef.current) {
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
            if (audioBlob.size > 0) sendAudioMessage(audioBlob);
        } else {
            dispatch({
                type: 'ADD_MESSAGE',
                payload: {
                  id: 'no-speech-' + Date.now(),
                  type: 'assistant',
                  content: 'I could not hear anything. Please try speaking again.',
                  timestamp: new Date(),
                },
              });
        }
        audioChunksRef.current = [];
        cleanupVAD();
      };
      mediaRecorderRef.current.start();
      startVoiceActivityDetection(stream);

    } catch (error) {
      console.error('Mic access error:', error);
      alert('Microphone access denied. Please check browser permissions.');
      dispatch({ type: 'SET_IS_RECORDING', payload: false });
    }
  };
  
  const sendAudioMessage = async (audioBlob: Blob) => {
    dispatch({ type: 'SET_IS_PROCESSING', payload: true });
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: '🎤 Voice Message...',
      timestamp: new Date(),
    };
    dispatch({ type: 'ADD_MESSAGE', payload: userMessage });
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data: ChatResponse = await response.json();
      dispatch({ 
        type: 'UPDATE_USER_VOICE_MESSAGE', 
        payload: { id: userMessage.id, content: data.transcription || 'Voice message', language: data.language } 
      });
      const assistantMessage: Message = {
        id: data.session_id,
        type: 'assistant',
        content: data.response,
        timestamp: new Date(),
        language: data.response_language || data.language,
        audioUrl: data.audio_url ? `${API_BASE}${data.audio_url}` : undefined,
      };
      dispatch({ type: 'ADD_MESSAGE', payload: assistantMessage });
      if (assistantMessage.audioUrl) playAudio(assistantMessage.audioUrl, assistantMessage.id);
    } catch (error) {
       console.error('Audio chat error:', error);
       dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          id: 'error-' + Date.now(),
          type: 'assistant',
          content: 'I had trouble understanding your voice. Could you please try again?',
          timestamp: new Date(),
        },
      });
    } finally {
      dispatch({ type: 'SET_IS_PROCESSING', payload: false });
    }
  };

  const formatTime = (date: Date) => {
    if (!isClient) return '';
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

return (
  <div className="flex flex-col h-screen w-screen bg-gradient-to-br from-slate-50 to-orange-50 dark:from-slate-900 dark:to-orange-900/20 overflow-hidden relative">
    <div 
      className={cn(
        'absolute inset-0 w-full h-full transition-opacity duration-1000 ease-in-out z-0 pointer-events-none',
        isGaneshaSpeaking ? 'opacity-100' : 'opacity-0'
      )}
    >
      <video
        ref={videoRefMobile}
        src="/video.mp4"
        loop
        muted
        playsInline
        className="absolute h-full w-full object-cover opacity-80 md:hidden"
      />
      <div className="hidden md:flex lg:hidden justify-center items-center w-full h-full">
        <div className="relative w-1/2 h-full">
            <video
              ref={videoRefTablet}
              src="/video.mp4"
              loop
              muted
              playsInline
              className="absolute h-full w-full object-cover object-top opacity-80"
            />
        </div>
      </div>
      <div className="hidden lg:flex justify-between items-end w-full h-full">
        <video
          ref={videoRefLeft}
          src="/video.mp4"
          loop
          muted
          playsInline
          className="h-full w-auto object-contain opacity-80"
        />
        <video
          ref={videoRefRight}
          src="/video.mp4"
          loop
          muted
          playsInline
          className="h-full w-auto object-contain opacity-80"
          style={{ transform: 'scaleX(-1)' }}
        />
      </div>
    </div>
    <div className="relative z-10 flex flex-col h-full bg-transparent">
      <header className="flex-shrink-0 bg-white/80 dark:bg-slate-950/80 backdrop-blur-lg border-b border-slate-200 dark:border-slate-800">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" className="rounded-full" onClick={() => router.push('/')}>
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div className="flex items-center gap-3">
                <Avatar className="h-11 w-11 border-2 border-orange-500/50">
                  <AvatarFallback className="bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400 text-2xl">🕉️</AvatarFallback>
                </Avatar>
                <div>
                  <h1 className="text-lg font-bold text-slate-900 dark:text-white">Lord Ganesha</h1>
                  <p className="text-sm text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                    Online
                  </p>
                </div>
              </div>
            </div>
            <Button variant="ghost" size="icon" className="rounded-full" onClick={toggleMute}>
              {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
            </Button>
          </div>
        </div>
      </header>
      <main className="flex-1 overflow-y-auto">
        <ScrollArea className="h-full">
          <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
            {messages.map((message) => (
              <div key={message.id} className={cn('flex items-end gap-3 w-full', message.type === 'user' ? 'justify-end' : 'justify-start')}>
                {message.type === 'assistant' && (
                  <Avatar className="h-8 w-8 flex-shrink-0">
                    <AvatarFallback className="bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400 text-lg">🕉️</AvatarFallback>
                  </Avatar>
                )}
                <div className={cn('flex flex-col gap-1 w-full', message.type === 'user' ? 'items-end' : 'items-start')}>
                  <div className={cn('max-w-md md:max-w-lg rounded-2xl px-4 py-2.5 shadow-sm break-words', 
                    message.type === 'user' ? 'bg-orange-600 text-white rounded-br-none' : 'bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700 rounded-bl-none'
                  )}>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                  </div>
                  <div className="flex items-center gap-2 px-1">
                    {message.language && <Badge variant="outline" className="text-xs h-5">{message.language.toUpperCase()}</Badge>}
                    {message.audioUrl && (
                      <Button variant="ghost" size="sm" className="h-6 px-1.5 text-xs text-slate-500 hover:text-slate-900" onClick={() => (isPlaying && playingMessageId === message.id) ? stopAudio() : playAudio(message.audioUrl!, message.id)}>
                        {(isPlaying && playingMessageId === message.id) ? <VolumeX className="w-3 h-3 mr-1" /> : <Volume2 className="w-3 h-3 mr-1" />}
                        Listen
                      </Button>
                    )}
                    <span className="text-xs text-slate-400 dark:text-slate-500">{formatTime(message.timestamp)}</span>
                  </div>
                </div>
                {message.type === 'user' && (
                  <Avatar className="h-8 w-8 flex-shrink-0">
                    <AvatarFallback className="bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 text-lg">👤</AvatarFallback>
                  </Avatar>
                )}
              </div>
            ))}

            {isProcessing && (
              <div className="flex items-end gap-3 w-full justify-start">
                <Avatar className="h-8 w-8 flex-shrink-0">
                  <AvatarFallback className="bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400 text-lg">🕉️</AvatarFallback>
                </Avatar>
                <div className="max-w-md md:max-w-lg rounded-2xl px-4 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-bl-none shadow-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse delay-150"></div>
                    <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse delay-300"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>
      </main>
      <footer className="flex-shrink-0 bg-white/80 dark:bg-slate-950/80 backdrop-blur-lg border-t border-slate-200 dark:border-slate-800">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <div className="flex items-center gap-2">
            <Input
              placeholder="Ask Ganesha a question..."
              value={textInput}
              onChange={(e) => dispatch({ type: 'SET_TEXT_INPUT', payload: e.target.value })}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendTextMessage(); }}}
              disabled={isProcessing || isRecording}
              className="flex-1 h-11 text-base rounded-full px-5"
            />
            <Button size="icon" className="h-11 w-11 rounded-full flex-shrink-0" onClick={sendTextMessage} disabled={isProcessing || isRecording || !textInput.trim()}>
              <Send className="w-5 h-5" />
            </Button>
            <Button
              size="icon"
              className={cn(
                'h-11 w-11 rounded-full flex-shrink-0 transition-colors',
                isRecording && voiceDetected && 'bg-green-600 hover:bg-green-700',
                isRecording && !voiceDetected && 'bg-red-600 hover:bg-red-700',
                !isRecording && 'bg-blue-600 hover:bg-blue-700'
              )}
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isProcessing}
            >
              {isRecording ? <MicOff className="w-5 h-5 animate-pulse" /> : <Mic className="w-5 h-5" />}
            </Button>
          </div>
          {isRecording && (
              <p className="text-xs text-center mt-2 font-medium text-slate-500">
                  {hasSpokenRef.current ? 'Recording stops on silence...' : 'Listening...'}
              </p>
          )}
        </div>
      </footer>
    </div>
  </div>
);
}