'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Send, Volume2, VolumeX, MessageCircle, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';

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
  user_message: string;
  response: string;
  language: string;
  response_language?: string;
  audio_url?: string;
}

interface ChatPageProps {
  onBackToHome: () => void;
}

export default function ChatPage({ onBackToHome }: ChatPageProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [textInput, setTextInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentAudio, setCurrentAudio] = useState<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playingMessageId, setPlayingMessageId] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(false);
  const [voiceDetected, setVoiceDetected] = useState(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    setIsClient(true);
    // Add welcome message from Lord Ganesha
    const welcomeMessage: Message = {
      id: 'welcome',
      type: 'assistant',
      content: '🕉️ Namaste! I am Lord Ganesha, the remover of obstacles and patron of arts and sciences.\\n\\nI am here to guide you with wisdom, bless your endeavors, and help you overcome any challenges you may face. Whether you seek spiritual guidance, need motivation for new beginnings, or simply wish to have a meaningful conversation, I am here for you.\\n\\nFeel free to speak in any Indian language or type in English. How may I bless you today? 🙏',
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Cleanup audio when component unmounts
  useEffect(() => {
    return () => {
      if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        setCurrentAudio(null);
        setIsPlaying(false);
        setPlayingMessageId(null);
      }
      
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
        silenceTimerRef.current = null;
      }
      
      if (audioContextRef.current) {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
    };
  }, [currentAudio]);

  // Enable audio context on first user interaction
  const enableAudio = async () => {
    if (!audioEnabled) {
      try {
        const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmEcBzaf2u/HeCEFKIXJ8d2OOAYOYL3r5ZBPFB5Ol9n1yXIqBSN8yO/HeCwFLoJI8+OQRA==');
        await audio.play();
        setAudioEnabled(true);
        console.log('✅ Audio context enabled');
      } catch (error) {
        console.log('Audio context not enabled yet');
      }
    }
  };

  const sendTextMessage = async () => {
    if (!textInput.trim()) return;
    
    await enableAudio();
    setIsProcessing(true);
    
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: textInput,
      timestamp: new Date(),
      language: 'en'
    };
    
    setMessages(prev => [...prev, userMessage]);
    const currentInput = textInput;
    setTextInput('');
    
    try {
      const formData = new FormData();
      formData.append('text', currentInput);
      formData.append('language', 'auto'); // Let backend detect language
      
      const response = await fetch('http://localhost:8000/text-chat', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      const ganesha_message: Message = {
        id: data.session_id,
        type: 'assistant',
        content: data.response,
        timestamp: new Date(),
        language: data.response_language || data.language,
        audioUrl: data.audio_url ? `http://localhost:8000${data.audio_url}` : undefined
      };
      
      setMessages(prev => [...prev, ganesha_message]);
      
      // Play audio response if available and not muted
      if (data.audio_url && !isMuted) {
        playAudio(`http://localhost:8000${data.audio_url}`, data.session_id);
      }
      
    } catch (error) {
      console.error('Text chat error:', error);
      setMessages(prev => [...prev, {
        id: 'error-' + Date.now(),
        type: 'assistant',
        content: 'I apologize, but I encountered an issue processing your message. Please try again.',
        timestamp: new Date(),
        language: 'en'
      }]);
    } finally {
      setIsProcessing(false);
    }
  };

  const startRecording = async () => {
    await enableAudio();
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      });
      
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      source.connect(analyserRef.current);
      
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });
      
      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };
      
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await sendAudioMessage(audioBlob);
        stream.getTracks().forEach(track => track.stop());
        
        if (audioContextRef.current) {
          audioContextRef.current.close();
          audioContextRef.current = null;
        }
        analyserRef.current = null;
      };
      
      mediaRecorderRef.current.start();
      setIsRecording(true);
      startVoiceActivityDetection();
      
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const startVoiceActivityDetection = () => {
    if (!analyserRef.current) return;
    
    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    let hasDetectedVoice = false;
    
    const checkAudioLevel = () => {
      if (!analyserRef.current || !isRecording) return;
      
      analyserRef.current.getByteFrequencyData(dataArray);
      
      const sum = dataArray.reduce((a, b) => a + b, 0);
      const averageVolume = sum / bufferLength;
      const rms = Math.sqrt(dataArray.reduce((a, b) => a + b * b, 0) / bufferLength);
      
      const VOICE_THRESHOLD = 20;
      const RMS_THRESHOLD = 12;
      const SILENCE_DURATION = 2000;
      
      const isVoiceDetected = averageVolume > VOICE_THRESHOLD || rms > RMS_THRESHOLD;
      
      if (isVoiceDetected) {
        hasDetectedVoice = true;
        if (!voiceDetected) {
          setVoiceDetected(true);
        }
        if (silenceTimerRef.current) {
          clearTimeout(silenceTimerRef.current);
          silenceTimerRef.current = null;
        }
      } else {
        if (voiceDetected) {
          setVoiceDetected(false);
        }
        
        if (hasDetectedVoice && !silenceTimerRef.current) {
          silenceTimerRef.current = setTimeout(() => {
            stopRecording();
          }, SILENCE_DURATION);
        }
      }
      
      if (isRecording) {
        requestAnimationFrame(checkAudioLevel);
      }
    };
    
    checkAudioLevel();
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
        silenceTimerRef.current = null;
      }
      
      setVoiceDetected(false);
      setIsRecording(false);
      
      try {
        mediaRecorderRef.current.stop();
      } catch (error) {
        console.error('Error stopping media recorder:', error);
      }
    }
  };

  const sendAudioMessage = async (audioBlob: Blob) => {
    setIsProcessing(true);
    
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: 'Voice message...',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob);

      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: ChatResponse = await response.json();
      
      setMessages(prev => 
        prev.map(msg => 
          msg.id === userMessage.id 
            ? { ...msg, content: result.user_message, language: result.language }
            : msg
        )
      );

      const assistantMessage: Message = {
        id: result.session_id,
        type: 'assistant',
        content: result.response,
        language: result.language,
        audioUrl: result.audio_url ? `http://localhost:8000${result.audio_url}` : undefined,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

      if (result.audio_url && !isMuted) {
        playAudio(`http://localhost:8000${result.audio_url}`, result.session_id);
      }

    } catch (error) {
      console.error('Error sending audio:', error);
      const errorMessage: Message = {
        id: 'error-' + Date.now(),
        type: 'assistant',
        content: 'I apologize, but I encountered an issue processing your message. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const playAudio = async (url: string, messageId?: string) => {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      setIsPlaying(false);
      setPlayingMessageId(null);
    }
    
    try {
      const audio = new Audio(url);
      audio.volume = 1.0;
      
      audio.onended = () => {
        setCurrentAudio(null);
        setIsPlaying(false);
        setPlayingMessageId(null);
      };
      
      await audio.play();
      setCurrentAudio(audio);
      setIsPlaying(true);
      if (messageId) setPlayingMessageId(messageId);
      
    } catch (error) {
      console.error('Audio play failed:', error);
      setIsPlaying(false);
      setPlayingMessageId(null);
      setCurrentAudio(null);
    }
  };

  const stopAudio = () => {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      setCurrentAudio(null);
      setIsPlaying(false);
      setPlayingMessageId(null);
    }
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
    if (currentAudio && !isMuted) {
      stopAudio();
    }
  };

  const formatTime = (date: Date) => {
    if (!isClient) return '';
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={onBackToHome}
                className="hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Home
              </Button>
              <div className="flex items-center gap-3">
                <Avatar className="h-10 w-10 bg-orange-600">
                  <AvatarFallback className="text-white font-bold">🕉️</AvatarFallback>
                </Avatar>
                <div>
                  <h1 className="text-lg font-bold text-slate-900 dark:text-white">
                    Lord Ganesha Assistant
                  </h1>
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    Divine guidance in your language
                  </p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {isPlaying && (
                <Button variant="outline" size="sm" onClick={stopAudio}>
                  <VolumeX className="h-4 w-4 mr-1" />
                  Stop
                </Button>
              )}
              <Button variant="outline" size="sm" onClick={toggleMute}>
                {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="max-w-5xl mx-auto px-4 py-6">
        <Card className="h-[calc(100vh-200px)] flex flex-col shadow-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
          <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
            {/* Messages */}
            <ScrollArea className="flex-1 px-4">
              <div className="space-y-6 py-4 max-w-full">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} w-full`}
                  >
                    <div className={`flex gap-3 max-w-[85%] min-w-0 ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                      <Avatar className="h-8 w-8 flex-shrink-0 mt-1">
                        <AvatarFallback className={`${
                          message.type === 'user' 
                            ? 'bg-blue-600 text-white text-sm' 
                            : 'bg-orange-600 text-white text-sm'
                        }`}>
                          {message.type === 'user' ? '👤' : '🕉️'}
                        </AvatarFallback>
                      </Avatar>
                      
                      <div className={`min-w-0 flex-1 ${message.type === 'user' ? 'flex flex-col items-end' : ''}`}>
                        <div className={`rounded-2xl px-4 py-3 shadow-sm break-words ${
                          message.type === 'user' 
                            ? 'bg-blue-600 text-white max-w-full' 
                            : 'bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700 max-w-full'
                        }`}>
                          <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                            {message.content}
                          </p>
                        </div>
                        
                        <div className={`flex items-center gap-2 mt-2 flex-wrap ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                          <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                            {formatTime(message.timestamp)}
                          </span>
                          
                          {message.language && (
                            <Badge variant="outline" className="text-xs h-5 border-orange-300 text-orange-700 dark:border-orange-700 dark:text-orange-300">
                              {message.language.toUpperCase()}
                            </Badge>
                          )}
                          
                          {message.audioUrl && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => playAudio(message.audioUrl!, message.id)}
                              className="h-6 px-2 text-xs hover:bg-orange-100 dark:hover:bg-orange-900/20 text-orange-600 dark:text-orange-400"
                            >
                              <Volume2 className="h-3 w-3 mr-1" />
                              Play
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {isProcessing && (
                  <div className="flex justify-start w-full">
                    <div className="flex gap-3 max-w-[85%]">
                      <Avatar className="h-8 w-8 flex-shrink-0 mt-1">
                        <AvatarFallback className="bg-orange-600 text-white text-sm">🕉️</AvatarFallback>
                      </Avatar>
                      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl px-4 py-3 shadow-sm">
                        <div className="flex items-center gap-3">
                          <div className="flex gap-1">
                            <div className="w-2 h-2 bg-orange-600 rounded-full animate-pulse"></div>
                            <div className="w-2 h-2 bg-orange-600 rounded-full animate-pulse delay-75"></div>
                            <div className="w-2 h-2 bg-orange-600 rounded-full animate-pulse delay-150"></div>
                          </div>
                          <span className="text-sm text-slate-600 dark:text-slate-400">Lord Ganesha is thinking...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div ref={messagesEndRef} />
            </ScrollArea>

            <Separator />

            {/* Input Area */}
            <div className="p-4 bg-slate-50 dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700">
              <div className="flex gap-2">
                <div className="flex-1 flex gap-2">
                  <Input
                    placeholder="🕉️ Share your thoughts with Lord Ganesha..."
                    value={textInput}
                    onChange={(e) => setTextInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendTextMessage();
                      }
                    }}
                    disabled={isProcessing}
                    className="flex-1 h-10 border-slate-200 dark:border-slate-700 focus:border-orange-500 dark:focus:border-orange-400"
                  />
                  <Button
                    onClick={sendTextMessage}
                    disabled={isProcessing || !textInput.trim()}
                    size="sm"
                    className="h-10 px-4 bg-orange-600 hover:bg-orange-700 text-white"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
                
                <Button
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={isProcessing}
                  variant={isRecording ? "destructive" : "default"}
                  size="sm"
                  className={`h-10 px-4 ${
                    isRecording 
                      ? `animate-pulse ${voiceDetected ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}` 
                      : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
                >
                  {isRecording ? (
                    <div className="flex items-center gap-1">
                      <MicOff className="h-4 w-4" />
                      {voiceDetected && <span className="w-1 h-1 bg-white rounded-full animate-pulse"></span>}
                    </div>
                  ) : (
                    <Mic className="h-4 w-4" />
                  )}
                </Button>
              </div>
              
              {isRecording && (
                <div className="mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                  <p className={`text-xs flex items-center justify-center gap-2 ${
                    voiceDetected 
                      ? 'text-green-700 dark:text-green-300' 
                      : 'text-blue-700 dark:text-blue-300'
                  }`}>
                    <Mic className={`h-3 w-3 ${voiceDetected ? 'animate-pulse text-green-600' : 'text-blue-600'}`} />
                    {voiceDetected ? (
                      <strong>🎙️ Voice detected - Keep speaking!</strong>
                    ) : (
                      <strong>⏱️ Recording... Will auto-stop after 2 seconds of silence</strong>
                    )}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
