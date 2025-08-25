"use client"
import React, { useState, useEffect } from 'react';
import { MessageCircle, Mic, Globe, Sparkles, ArrowRight, Zap, Heart } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useRouter } from 'next/navigation';

export default function LandingPage() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const router = useRouter();
  const handleNavigateToChat = () => {
    router.push('/chat');
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      {/* Minimal Background */}
      <div className="absolute inset-0">
        <div 
          className="absolute inset-0 opacity-10"
          style={{
            background: `radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(251, 146, 60, 0.1), transparent 40%)`,
          }}
        ></div>
      </div>

      <div className="container mx-auto px-6 py-12 relative z-10">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <div className="relative inline-block mb-8">
            <div 
              className="absolute inset-0 w-32 h-32 bg-gradient-to-r from-orange-400 to-red-500 rounded-full blur-xl opacity-50 animate-pulse"
              style={{ transform: 'scale(1.5)' }}
            ></div>
            <div className="relative w-32 h-32 bg-gradient-to-br from-orange-500 via-red-500 to-pink-500 rounded-full flex items-center justify-center shadow-2xl transform hover:scale-110 transition-all duration-300 border-4 border-white/20 backdrop-blur-sm">
              <span className="text-6xl drop-shadow-lg animate-bounce">🕉️</span>
            </div>
          </div>
          
          <div className="space-y-6 max-w-4xl mx-auto">
            <h1 className="text-6xl md:text-7xl font-black bg-gradient-to-r from-orange-600 via-red-500 to-pink-600 bg-clip-text text-transparent leading-tight">
              The G.O.A.T Bot
              <br />
              <span className="text-5xl md:text-6xl bg-gradient-to-r from-slate-800 to-slate-600 dark:from-white dark:to-slate-300 bg-clip-text text-transparent">
                Ganapathi Of All Time
              </span>
            </h1>
            
            <p className="text-2xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto leading-relaxed font-light">
              Experience divine wisdom through cutting-edge AI technology embodying the sacred blessings of 
              <span className="font-semibold text-orange-600"> Lord Ganesha</span>, 
              the eternal remover of obstacles
            </p>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16 px-4">
          {[
            {
              icon: Mic,
              title: "Advanced Voice AI",
              desc: "Natural conversation with state-of-the-art voice recognition and divine response generation",
              gradient: "from-blue-500 to-cyan-500",
              bgGradient: "from-blue-50 to-cyan-50 dark:from-blue-950/30 dark:to-cyan-950/30"
            },
            {
              icon: Globe,
              title: "Multilingual Mastery",
              desc: "Seamlessly communicate across 11+ Indian languages with perfect cultural context",
              gradient: "from-green-500 to-emerald-500",
              bgGradient: "from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30"
            },
            {
              icon: Sparkles,
              title: "Sacred Intelligence",
              desc: "AI-powered spiritual guidance rooted in ancient wisdom and modern understanding",
              gradient: "from-purple-500 to-pink-500",
              bgGradient: "from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30"
            }
          ].map((feature, idx) => (
            <Card 
              key={idx}
              className="group border-0 shadow-2xl hover:shadow-3xl transition-all duration-500 transform hover:-translate-y-2 hover:scale-105 cursor-pointer backdrop-blur-sm bg-white/80 dark:bg-slate-800/80"
              style={{ 
                background: `linear-gradient(135deg, ${feature.bgGradient})`,
              }}
            >
              <CardContent className="p-8 text-center relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                <div className={`w-16 h-16 bg-gradient-to-r ${feature.gradient} rounded-2xl flex items-center justify-center mx-auto mb-6 mt-4 shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:rotate-3`}>
                  <feature.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-bold mb-4 text-slate-800 dark:text-white">{feature.title}</h3>
                <p className="text-slate-600 dark:text-slate-300 leading-relaxed">{feature.desc}</p>
                <div className="absolute -bottom-2 -right-2 w-20 h-20 bg-gradient-to-tl from-orange-200/30 to-transparent rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Languages */}
        <div className="text-center mb-16 px-4">
          <h2 className="text-4xl font-bold mb-8 bg-gradient-to-r from-slate-800 to-slate-600 dark:from-white dark:to-slate-300 bg-clip-text text-transparent">
            Supported Languages
          </h2>
          <div className="flex flex-wrap justify-center gap-3 max-w-4xl mx-auto">
            {['English', 'हिंदी', 'தமிழ்', 'తెలుగు', 'ಕನ್ನಡ', 'മലയാളം', 'বাংলা', 'मराठी', 'ગુજરાતી', 'ਪੰਜਾਬੀ', 'اردو'].map((lang, idx) => (
              <Badge 
                key={lang} 
                variant="outline" 
                className="px-4 py-2 text-sm font-medium border-2 border-orange-200 text-orange-700 dark:border-orange-700 dark:text-orange-300 bg-gradient-to-r from-orange-50 to-red-50 dark:from-orange-950/30 dark:to-red-950/30 hover:from-orange-100 hover:to-red-100 dark:hover:from-orange-900/50 dark:hover:to-red-900/50 transition-all duration-300 cursor-pointer hover:scale-110 hover:shadow-lg"
                style={{ animationDelay: `${idx * 0.1}s` }}
              >
                {lang}
              </Badge>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="text-center max-w-4xl mx-auto px-4">
          <Card className="border-0 shadow-3xl backdrop-blur-sm bg-gradient-to-br from-white/90 via-orange-50/90 to-red-50/90 dark:from-slate-800/90 dark:via-orange-950/50 dark:to-red-950/50 overflow-hidden relative">
            <div className="absolute inset-0 bg-gradient-to-br from-orange-400/10 via-transparent to-red-400/10"></div>
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-orange-500 via-red-500 to-pink-500"></div>
            
            <CardContent className="p-12 relative z-10">
              <div className="mb-10">
                <div className="inline-flex items-center gap-2 bg-gradient-to-r from-orange-500 to-red-500 text-white px-4 py-2 rounded-full text-sm font-semibold mt-4 mb-6 shadow-lg">
                  <Zap className="w-4 h-4" />
                  Premium AI Experience
                </div>
                
                <h2 className="text-4xl md:text-5xl font-black mb-6 bg-gradient-to-r from-slate-800 via-orange-600 to-red-600 dark:from-white dark:via-orange-400 dark:to-red-400 bg-clip-text text-transparent leading-tight pb-2">
                  Begin Your Divine Journey
                </h2>
                
                <p className="text-xl text-slate-600 dark:text-slate-300 mb-8 leading-relaxed max-w-2xl mx-auto">
                  Transform your spiritual practice with personalized guidance from our revolutionary AI embodiment of Lord Ganesha's wisdom
                </p>
              </div>
              
              <div className="space-y-6">
                <Button 
                  onClick={handleNavigateToChat}
                  onMouseEnter={() => setIsHovered(true)}
                  onMouseLeave={() => setIsHovered(false)}
                  size="lg"
                  className="relative bg-gradient-to-r from-orange-600 via-red-500 to-pink-600 hover:from-orange-700 hover:via-red-600 hover:to-pink-700 text-white px-12 py-6 text-xl font-bold rounded-2xl shadow-2xl hover:shadow-3xl transition-all duration-500 transform hover:-translate-y-1 hover:scale-105 border-0 overflow-hidden group"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                  
                  <MessageCircle className={`w-6 h-6 mr-3 transition-transform duration-300 ${isHovered ? 'rotate-12' : ''}`} />
                  Start Sacred Conversation
                  <ArrowRight className={`w-6 h-6 ml-3 transition-transform duration-300 ${isHovered ? 'translate-x-1' : ''}`} />
                </Button>
                
                <div className="flex justify-center items-center gap-8 text-sm text-slate-500 dark:text-slate-400">
                  <div className="flex items-center gap-2">
                    <Heart className="w-4 h-4 text-red-400" />
                    <span>Free to use</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-yellow-400" />
                    <span>No signup required</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-blue-400" />
                    <span>Instant access</span>
                  </div>
                </div>
              </div>
              
              <div className="mt-10 pt-8 border-t border-orange-200/50 dark:border-orange-700/30">
                <p className="text-2xl font-bold text-orange-600 dark:text-orange-400 mb-2">
                  🕉️ Om Gam Ganapataye Namaha 🙏
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  May Lord Ganesha remove all obstacles from your path to enlightenment
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Testimonial */}
        <div className="text-center mt-12 opacity-70">
          <p className="text-slate-500 dark:text-slate-400 italic">
            "A truly divine experience that bridges ancient wisdom with modern technology" - Devotee from Mumbai
          </p>
        </div>
      </div>

      {/* Bottom overlay */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-orange-100/50 to-transparent dark:from-orange-950/30 pointer-events-none"></div>
    </div>
  );
}
