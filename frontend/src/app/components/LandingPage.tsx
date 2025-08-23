'use client';

import React from 'react';
import { MessageCircle, Mic, Globe, Sparkles, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface LandingPageProps {
  onStartChat: () => void;
}

interface LandingPageProps {
  onNavigateToChat: () => void;
}

export default function LandingPage({ onNavigateToChat }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 dark:from-slate-950 dark:to-slate-900">
      {/* Header */}
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-orange-600 rounded-full mb-6">
            <span className="text-3xl">🕉️</span>
          </div>
          <h1 className="text-5xl font-bold text-slate-900 dark:text-white mb-4">
            Lord Ganesha
            <span className="text-orange-600"> Voice Assistant</span>
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Seek divine wisdom and guidance through our AI-powered voice chatbot embodying the blessings of Lord Ganesha, the remover of obstacles.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <Card className="border-orange-200 dark:border-orange-800 hover:shadow-lg transition-shadow">
            <CardContent className="p-6 text-center">
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Mic className="w-6 h-6 text-orange-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Voice Interaction</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">
                Speak naturally and receive divine responses with auto voice detection
              </p>
            </CardContent>
          </Card>

          <Card className="border-orange-200 dark:border-orange-800 hover:shadow-lg transition-shadow">
            <CardContent className="p-6 text-center">
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Globe className="w-6 h-6 text-orange-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Multilingual Support</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">
                Communicate in Hindi, Tamil, Telugu, and 8+ Indian languages
              </p>
            </CardContent>
          </Card>

          <Card className="border-orange-200 dark:border-orange-800 hover:shadow-lg transition-shadow">
            <CardContent className="p-6 text-center">
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-6 h-6 text-orange-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Divine Wisdom</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">
                Get spiritual guidance, motivation, and obstacle-removing blessings
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Supported Languages */}
        <div className="text-center mb-12">
          <h2 className="text-2xl font-semibold mb-6">Supported Languages</h2>
          <div className="flex flex-wrap justify-center gap-2">
            {['English', 'हिंदी', 'தமிழ்', 'తెలుగు', 'ಕನ್ನಡ', 'മലയാളം', 'বাংলা', 'मराठी', 'ગુજરાતી', 'ਪੰਜਾਬੀ', 'اردو'].map((lang) => (
              <Badge key={lang} variant="outline" className="border-orange-300 text-orange-700">
                {lang}
              </Badge>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <Card className="max-w-2xl mx-auto border-orange-200 dark:border-orange-800">
            <CardContent className="p-8">
              <div className="mb-6">
                <h2 className="text-2xl font-bold mb-2">Begin Your Divine Journey</h2>
                <p className="text-slate-600 dark:text-slate-400">
                  Start your conversation with Lord Ganesha and receive personalized spiritual guidance
                </p>
              </div>
              
              <Button 
                onClick={onNavigateToChat}
                size="lg"
                className="bg-orange-600 hover:bg-orange-700 text-white px-8 py-4 text-lg font-medium"
              >
                <MessageCircle className="w-5 h-5 mr-2" />
                Start Sacred Conversation
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-4">
                🕉️ Om Gam Ganapataye Namaha 🙏
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
