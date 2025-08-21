'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Send, Volume2, VolumeX, MessageCircle, Sparkles, Heart } from 'lucide-react';
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
  audio_url?: string;
}

export default function GaneshaChatbot() {
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
      content: '🕉️ Namaste! I am Lord Ganesha, the remover of obstacles and patron of arts and sciences.\n\nI am here to guide you with wisdom, bless your endeavors, and help you overcome any challenges you may face. Whether you seek spiritual guidance, need motivation for new beginnings, or simply wish to have a meaningful conversation, I am here for you.\n\nFeel free to speak in any Indian language or type in English. How may I bless you today? 🙏',
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
      
      // Cleanup voice activity detection
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
        // Create a silent audio to enable audio context
        const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmEcBzaf2u/HeCEFKIXJ8d2OOAYOYL3r5ZBPFB5Ol9n1yXIqBSN8yO/HeCwFLoJI8+OQRA==');
        await audio.play();
        setAudioEnabled(true);
        console.log('✅ Audio context enabled');
      } catch (error) {
        console.log('Audio context not enabled yet');
      }
    }
  };

  const startRecording = async () => {
    // Enable audio on user interaction
    await enableAudio();
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      });
      
      // Set up audio context for voice activity detection
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
        
        // Clean up audio context
        if (audioContextRef.current) {
          audioContextRef.current.close();
          audioContextRef.current = null;
        }
        analyserRef.current = null;
      };
      
      mediaRecorderRef.current.start();
      setIsRecording(true);
      
      // Start voice activity detection
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
    
    const checkAudioLevel = () => {
      if (!analyserRef.current || !isRecording) return;
      
      analyserRef.current.getByteFrequencyData(dataArray);
      
      // Calculate average volume
      const sum = dataArray.reduce((a, b) => a + b, 0);
      const averageVolume = sum / bufferLength;
      
      // Voice activity threshold (adjust as needed)
      const VOICE_THRESHOLD = 30; // Adjust this value to fine-tune sensitivity
      const SILENCE_DURATION = 2000; // 2 seconds of silence before auto-stop
      
      console.log('Audio level:', averageVolume);
      
      if (averageVolume > VOICE_THRESHOLD) {
        // Voice detected, clear silence timer
        if (!voiceDetected) {
          setVoiceDetected(true);
        }
        if (silenceTimerRef.current) {
          clearTimeout(silenceTimerRef.current);
          silenceTimerRef.current = null;
        }
      } else {
        // Silence detected, start timer if not already started
        if (voiceDetected) {
          setVoiceDetected(false);
        }
        if (!silenceTimerRef.current) {
          console.log('Silence detected, starting timer...');
          silenceTimerRef.current = setTimeout(() => {
            console.log('Auto-stopping recording due to silence');
            stopRecording();
          }, SILENCE_DURATION);
        }
      }
      
      // Continue monitoring if still recording
      if (isRecording) {
        requestAnimationFrame(checkAudioLevel);
      }
    };
    
    checkAudioLevel();
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      console.log('Stopping recording...');
      
      // Clear silence timer
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
        silenceTimerRef.current = null;
      }
      
      setVoiceDetected(false);
      
      mediaRecorderRef.current.stop();
      setIsRecording(false);
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
      
      // Update user message with transcription
      setMessages(prev => 
        prev.map(msg => 
          msg.id === userMessage.id 
            ? { ...msg, content: result.user_message, language: result.language }
            : msg
        )
      );

      // Add assistant response
      const assistantMessage: Message = {
        id: result.session_id,
        type: 'assistant',
        content: result.response,
        language: result.language,
        audioUrl: result.audio_url ? `http://localhost:8000${result.audio_url}` : undefined,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Play audio response if available and not muted
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

  const sendTextMessage = async () => {
    if (!textInput.trim()) return;
    
    // Enable audio on user interaction
    await enableAudio();
    
    setIsProcessing(true);
    
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: textInput,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setTextInput('');

    try {
      const response = await fetch('http://localhost:8000/text-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: textInput,
          language: 'en'
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: ChatResponse = await response.json();

      const assistantMessage: Message = {
        id: result.session_id,
        type: 'assistant',
        content: result.response,
        language: result.language,
        audioUrl: result.audio_url ? `http://localhost:8000${result.audio_url}` : undefined,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Play audio response if available and not muted
      if (result.audio_url && !isMuted) {
        playAudio(`http://localhost:8000${result.audio_url}`, result.session_id);
      }

    } catch (error) {
      console.error('Error sending text:', error);
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
    console.log('🔊 Attempting to play audio:', url);
    
    // Stop any currently playing audio
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      setIsPlaying(false);
      setPlayingMessageId(null);
    }
    
    try {
      const audio = new Audio(url);
      
      // Ensure maximum volume for better audibility
      audio.volume = 1.0;
      
      // Add comprehensive event handlers
      audio.onloadstart = () => {
        console.log('Audio loading started...');
        setIsPlaying(true);
        if (messageId) setPlayingMessageId(messageId);
      };
      
      audio.oncanplay = () => console.log('Audio can start playing');
      audio.oncanplaythrough = () => console.log('Audio loaded successfully, ready to play');
      
      audio.onerror = (e) => {
        console.error('Audio playback error:', e);
        console.error('Audio error details:', audio.error);
        setIsPlaying(false);
        setPlayingMessageId(null);
        setCurrentAudio(null);
        alert(`Audio playback failed: ${audio.error?.message || 'Unknown error'}. Please check your audio settings.`);
      };
      
      audio.onended = () => {
        console.log('Audio playback completed - auto stopping');
        setCurrentAudio(null);
        setIsPlaying(false);
        setPlayingMessageId(null);
      };
      
      audio.onplay = () => {
        console.log('Audio started playing');
        setIsPlaying(true);
        if (messageId) setPlayingMessageId(messageId);
      };
      
      audio.onpause = () => {
        console.log('Audio paused');
        setIsPlaying(false);
        setPlayingMessageId(null);
      };
      
      // Auto-cleanup when audio stops/ends
      audio.addEventListener('ended', () => {
        console.log('🔇 Audio ended - cleaning up');
        audio.remove?.(); // Clean up audio element
        setCurrentAudio(null);
        setIsPlaying(false);
        setPlayingMessageId(null);
      });
      
      // Wait for audio to be ready
      await new Promise((resolve, reject) => {
        audio.addEventListener('canplaythrough', resolve, { once: true });
        audio.addEventListener('error', reject, { once: true });
        
        // Try to load the audio
        audio.load();
      });
      
      // Attempt to play
      console.log('🎵 Starting audio playback...');
      await audio.play();
      
      console.log('✅ Audio playback started successfully');
      setCurrentAudio(audio);
      setIsPlaying(true);
      if (messageId) setPlayingMessageId(messageId);
      
    } catch (error: any) {
      console.error('❌ Audio play failed:', error);
      setIsPlaying(false);
      setPlayingMessageId(null);
      setCurrentAudio(null);
      
      if (error.name === 'NotAllowedError') {
        alert('Audio playback blocked by browser. Please click anywhere on the page first, then try again.');
      } else if (error.name === 'AbortError') {
        console.log('Audio play was aborted (probably due to new audio starting)');
      } else {
        alert(`Could not play audio: ${error.message}. Please check your browser audio permissions.`);
      }
    }
  };

  const stopAudio = () => {
    if (currentAudio) {
      console.log('🔇 Manually stopping audio');
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
      stopAudio(); // Use the new stopAudio function
    }
  };

  const formatTime = (date: Date) => {
    if (!isClient) return '';
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-red-50 to-yellow-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-800">
      {/* Header */}
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-orange-200 dark:border-slate-700 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Avatar className="h-12 w-12 bg-gradient-to-r from-orange-500 to-red-500 ring-2 ring-orange-200 dark:ring-orange-800">
                  <AvatarFallback className="text-white font-bold text-lg">🕉️</AvatarFallback>
                </Avatar>
                <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white dark:border-slate-900"></div>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                  Lord Ganesha Assistant
                </h1>
                <p className="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                  Multilingual Voice & Text Chat • Always Available
                  {isPlaying && (
                    <span className="flex items-center gap-1 text-orange-600 dark:text-orange-400">
                      <Volume2 className="h-3 w-3 animate-pulse" />
                      <span className="text-xs font-medium">Playing Divine Voice</span>
                    </span>
                  )}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {isPlaying && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={stopAudio}
                  className="h-10 px-4 border-2 border-red-200 text-red-600 hover:bg-red-50 dark:border-red-800 dark:text-red-400 dark:hover:bg-red-900/20"
                >
                  <VolumeX className="h-4 w-4 mr-2 animate-pulse" />
                  Stop Audio
                </Button>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={toggleMute}
                className="h-10 px-4 border-2 hover:bg-orange-50 dark:hover:bg-orange-900/20"
              >
                {isMuted ? <VolumeX className="h-4 w-4 mr-2" /> : <Volume2 className="h-4 w-4 mr-2" />}
                {isMuted ? 'Unmute' : 'Mute'}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="max-w-5xl mx-auto px-4 py-6">
        <Card className="h-[calc(100vh-200px)] flex flex-col shadow-lg border-0 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm">
          <CardHeader className="pb-4 bg-gradient-to-r from-orange-500/10 to-red-500/10 dark:from-orange-500/20 dark:to-red-500/20 rounded-t-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-500 rounded-full">
                <MessageCircle className="h-5 w-5 text-white" />
              </div>
              <div>
                <CardTitle className="text-lg bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                  Sacred Conversation with Lord Ganesha
                </CardTitle>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                  Remover of obstacles • Patron of arts and sciences • Lord of beginnings
                </p>
              </div>
            </div>
          </CardHeader>
          
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
                      <Avatar className="h-9 w-9 flex-shrink-0 mt-1 ring-2 ring-offset-2 ring-offset-transparent">
                        <AvatarFallback className={`${
                          message.type === 'user' 
                            ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white text-sm' 
                            : 'bg-gradient-to-r from-orange-500 to-red-500 text-white text-sm'
                        }`}>
                          {message.type === 'user' ? '👤' : '🕉️'}
                        </AvatarFallback>
                      </Avatar>
                      
                      <div className={`min-w-0 flex-1 ${message.type === 'user' ? 'flex flex-col items-end' : ''}`}>
                        <div className={`rounded-2xl px-4 py-3 shadow-sm break-words hyphens-auto word-wrap-break-word ${
                          message.type === 'user' 
                            ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white max-w-full shadow-blue-200 dark:shadow-blue-900/50' 
                            : 'bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700 max-w-full shadow-orange-100 dark:shadow-orange-900/20'
                        }`}>
                          <p className="text-sm leading-relaxed whitespace-pre-wrap break-words overflow-wrap-anywhere word-break-break-word">
                            {message.content}
                          </p>
                        </div>
                        
                        <div className={`flex items-center gap-2 mt-2 flex-wrap ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                          <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                            {formatTime(message.timestamp)}
                          </span>
                          
                          {message.language && (
                            <Badge variant="outline" className="text-xs h-5 border-orange-200 text-orange-700 dark:border-orange-700 dark:text-orange-300">
                              {message.language.toUpperCase()}
                            </Badge>
                          )}
                          
                          {message.audioUrl && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={async () => {
                                if (playingMessageId === message.id && isPlaying) {
                                  stopAudio();
                                } else {
                                  await enableAudio();
                                  playAudio(message.audioUrl!, message.id);
                                }
                              }}
                              className={`h-6 px-2 text-xs hover:bg-orange-100 dark:hover:bg-orange-900/20 ${
                                playingMessageId === message.id && isPlaying 
                                  ? 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20' 
                                  : 'text-orange-600 dark:text-orange-400'
                              }`}
                            >
                              {playingMessageId === message.id && isPlaying ? (
                                <>
                                  <VolumeX className="h-3 w-3 mr-1 animate-pulse" />
                                  Stop Audio
                                </>
                              ) : (
                                <>
                                  <Volume2 className="h-3 w-3 mr-1" />
                                  Play Divine Voice
                                </>
                              )}
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
                      <Avatar className="h-9 w-9 flex-shrink-0 mt-1">
                        <AvatarFallback className="bg-orange-500 text-white text-sm">🕉️</AvatarFallback>
                      </Avatar>
                      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl px-4 py-3 shadow-sm">
                        <div className="flex items-center gap-3">
                          <div className="flex gap-1">
                            <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></div>
                            <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse delay-75"></div>
                            <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse delay-150"></div>
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
            <div className="p-6 bg-slate-50/50 dark:bg-slate-800/50 rounded-b-lg">
              <div className="flex gap-3">
                <div className="flex-1 flex gap-2">
                  <div className="relative flex-1">
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
                      className="flex-1 h-12 px-4 text-base border-2 border-slate-200 dark:border-slate-700 focus:border-orange-500 dark:focus:border-orange-400 rounded-xl bg-white dark:bg-slate-900"
                    />
                  </div>
                  <Button
                    onClick={sendTextMessage}
                    disabled={isProcessing || !textInput.trim()}
                    size="lg"
                    className="h-12 px-6 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white shadow-lg rounded-xl"
                  >
                    <Send className="h-5 w-5" />
                  </Button>
                </div>
                
                <Button
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={isProcessing}
                  variant={isRecording ? "destructive" : "default"}
                  size="lg"
                  className={`h-12 px-6 rounded-xl shadow-lg ${
                    isRecording 
                      ? `animate-pulse ${voiceDetected ? 'bg-green-500 hover:bg-green-600' : 'bg-red-500 hover:bg-red-600'}` 
                      : 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white'
                  }`}
                >
                  {isRecording ? (
                    <div className="flex items-center gap-2">
                      <MicOff className="h-5 w-5" />
                      {voiceDetected && <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>}
                    </div>
                  ) : (
                    <Mic className="h-5 w-5" />
                  )}
                </Button>
              </div>
              
              <div className="mt-4 text-center">
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  🎯 <strong>Speak in any Indian language</strong> or type in English • 🎤 Click microphone for voice message
                </p>
                
                {isRecording && (
                  <div className="mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <p className={`text-xs flex items-center justify-center gap-2 ${
                      voiceDetected 
                        ? 'text-green-700 dark:text-green-300' 
                        : 'text-blue-700 dark:text-blue-300'
                    }`}>
                      <Mic className={`h-4 w-4 ${voiceDetected ? 'animate-pulse text-green-500' : 'text-blue-500'}`} />
                      {voiceDetected ? (
                        <strong>🎙️ Voice detected - Keep speaking!</strong>
                      ) : (
                        <strong>⏱️ Recording... Will auto-stop after 2 seconds of silence</strong>
                      )}
                    </p>
                  </div>
                )}
                
                {!audioEnabled && !isRecording && (
                  <div className="mt-2 p-2 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                    <p className="text-xs text-amber-700 dark:text-amber-300 flex items-center justify-center gap-2">
                      <Volume2 className="h-4 w-4" />
                      <strong>Audio Ready:</strong> Click anywhere to enable Lord Ganesha's divine voice responses
                    </p>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
