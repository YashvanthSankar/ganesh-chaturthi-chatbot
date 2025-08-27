"use client"
import React, { useState, useEffect } from 'react';
import { MessageCircle, Mic, Globe, Sparkles, ArrowRight, Zap, Heart } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useRouter } from 'next/navigation';
import { ThemeToggle } from '@/components/ui/theme-toggle'; // Make sure this path is correct

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
    // --- Dark Mode Enhancement: Deeper, warmer background gradient for a divine feel ---
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-gray-50 via-white to-orange-50 dark:from-slate-900 dark:via-gray-900 dark:to-orange-950/50">
      
      {/* --- Added Theme Toggle for easy switching --- */}
      <div className="absolute top-4 right-4 z-20">
        <ThemeToggle />
      </div>

      <div className="absolute inset-0">
        <div 
          className="absolute inset-0 opacity-10"
          style={{
            background: `radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(251, 146, 60, 0.1), transparent 40%)`,
          }}
        ></div>
      </div>

      <div className="container mx-auto px-4 sm:px-6 py-8 md:py-12 relative z-10">
        {/* Hero Section */}
        <div className="text-center mb-12 md:mb-16">
          <div className="relative inline-block mb-8">
            {/* --- Dark Mode Enhancement: More vibrant glow --- */}
            <div 
              className="absolute inset-0 w-24 h-24 md:w-32 md:h-32 bg-gradient-to-r from-orange-400 to-red-500 rounded-full blur-2xl opacity-50 dark:opacity-70 animate-pulse"
              style={{ transform: 'scale(1.5)' }}
            ></div>
            <div className="relative w-24 h-24 md:w-32 md:h-32 bg-gradient-to-br from-orange-500 via-red-500 to-pink-500 rounded-full flex items-center justify-center shadow-2xl transform hover:scale-110 transition-all duration-300 border-4 border-white/20 backdrop-blur-sm">
              <span className="text-5xl md:text-6xl drop-shadow-lg animate-bounce">🕉️</span>
            </div>
          </div>
          
          <div className="space-y-6 max-w-4xl mx-auto">
            {/* --- Dark Mode Enhancement: Brighter text gradient for better contrast --- */}
            <h1 className="text-4xl md:text-7xl font-black bg-gradient-to-r from-orange-600 via-red-500 to-pink-600 dark:from-orange-500 dark:via-red-500 dark:to-pink-500 bg-clip-text text-transparent leading-tight">
              The G.O.A.T Bot
              <br />
              {/* --- Dark Mode Enhancement: Clean white-to-gold gradient --- */}
              <span className="text-3xl md:text-6xl bg-gradient-to-r from-slate-800 to-slate-600 dark:from-white dark:to-amber-200 bg-clip-text text-transparent">
                Ganapathi Of All Time
              </span>
            </h1>
            <p className="text-base md:text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto px-4">
              Experience divine wisdom through cutting-edge AI technology embodying the sacred blessings of 
              <span className="font-semibold text-orange-600 dark:text-orange-400"> Lord Ganesha</span>, 
              the eternal remover of obstacles
            </p>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-6 md:gap-8 mb-12 md:mb-16 px-4">
          {[
            {
              icon: Mic,
              title: "Advanced Voice AI",
              desc: "Natural conversation with state-of-the-art voice recognition and divine response generation",
              gradient: "from-blue-500 to-cyan-500",
            },
            {
              icon: Globe,
              title: "Multilingual Mastery",
              desc: "Seamlessly communicate across 11+ Indian languages with perfect cultural context",
              gradient: "from-green-500 to-emerald-500",
            },
            {
              icon: Sparkles,
              title: "Sacred Intelligence",
              desc: "AI-powered spiritual guidance rooted in ancient wisdom and modern understanding",
              gradient: "from-purple-500 to-pink-500",
            }
          ].map((feature, idx) => (
            // --- Dark Mode Enhancement: Subtle border to lift cards from the background ---
            <Card 
              key={idx}
              className="group border-0 dark:border dark:border-white/10 shadow-xl hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2 hover:scale-105 cursor-pointer backdrop-blur-sm bg-white/60 dark:bg-slate-800/60"
            >
              <CardContent className="p-6 md:p-8 text-center relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                <div className={`w-14 h-14 md:w-16 md:h-16 bg-gradient-to-r ${feature.gradient} rounded-2xl flex items-center justify-center mx-auto mb-6 mt-4 shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:rotate-3`}>
                  <feature.icon className="w-7 h-7 md:w-8 md:h-8 text-white" />
                </div>
                <h3 className="text-lg md:text-xl font-bold mb-4 text-slate-800 dark:text-white">{feature.title}</h3>
                <p className="text-sm md:text-base text-slate-600 dark:text-slate-300 leading-relaxed">{feature.desc}</p>
                <div className="absolute -bottom-2 -right-2 w-20 h-20 bg-gradient-to-tl from-orange-200/30 to-transparent rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Languages */}
        <div className="text-center mb-12 md:mb-16 px-4">
          <h2 className="text-3xl md:text-4xl font-bold mb-8 bg-gradient-to-r from-slate-800 to-slate-600 dark:from-white dark:to-slate-300 bg-clip-text text-transparent">
            Supported Languages
          </h2>
          <div className="flex flex-wrap justify-center gap-2 md:gap-3 max-w-4xl mx-auto">
            {['English', 'हिंदी', 'தமிழ்', 'తెలుగు', 'ಕನ್ನಡ', 'മലയാളം', 'বাংলা', 'मराठी', 'ગુજરાતી', 'ਪੰਜਾਬੀ', 'اردو'].map((lang, idx) => (
              <Badge 
                key={lang} 
                variant="outline" 
                className="px-3 py-1.5 md:px-4 md:py-2 text-xs md:text-sm font-medium border-2 border-orange-200 text-orange-700 dark:border-orange-700 dark:text-orange-300 bg-white/50 dark:bg-orange-950/30 hover:bg-orange-50/50 dark:hover:bg-orange-900/50 transition-all duration-300 cursor-pointer hover:scale-110 hover:shadow-lg"
                style={{ animationDelay: `${idx * 0.1}s` }}
              >
                {lang}
              </Badge>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="text-center max-w-4xl mx-auto px-4">
          {/* --- Dark Mode Enhancement: Richer gradient and subtle border --- */}
          <Card className="border-0 dark:border dark:border-white/10 shadow-2xl backdrop-blur-sm bg-gradient-to-br from-white/80 via-orange-50/80 to-red-50/80 dark:from-slate-800/80 dark:via-orange-950/50 dark:to-red-950/50 overflow-hidden relative">
            <div className="absolute inset-0 bg-gradient-to-br from-orange-400/10 via-transparent to-red-400/10"></div>
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-orange-500 via-red-500 to-pink-500"></div>
            
            <CardContent className="p-6 md:p-12 relative z-10">
              <div className="mb-8 md:mb-10">
                {/* <div className="inline-flex items-center gap-2 bg-gradient-to-r from-orange-500 to-red-500 text-white px-4 py-2 rounded-full text-sm font-semibold mt-4 mb-6 shadow-lg">
                  <Zap className="w-4 h-4" />
                  Premium AI Experience
                </div> */}
                
                <h2 className="text-3xl md:text-5xl font-black mb-6 bg-gradient-to-r from-slate-800 via-orange-600 to-red-600 dark:from-white dark:via-orange-400 dark:to-red-400 bg-clip-text text-transparent leading-tight pb-2">
                  Begin Your Divine Journey
                </h2>
                
                <p className="text-lg md:text-xl text-slate-600 dark:text-slate-300 mb-8 leading-relaxed max-w-2xl mx-auto">
                  Transform your spiritual practice with personalized guidance from our revolutionary AI embodiment of Lord Ganesha&apos;s wisdom
                </p>
              </div>
              
              <div className="space-y-6">
                <Button 
                  onClick={handleNavigateToChat}
                  onMouseEnter={() => setIsHovered(true)}
                  onMouseLeave={() => setIsHovered(false)}
                  size="lg"
                  className="relative w-full sm:w-auto bg-gradient-to-r from-orange-600 via-red-500 to-pink-600 hover:from-orange-700 hover:via-red-600 hover:to-pink-700 text-white px-8 py-5 md:px-12 md:py-6 text-lg md:text-xl font-bold rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-1 hover:scale-105 border-0 overflow-hidden group"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                  
                  <MessageCircle className={`w-5 h-5 md:w-6 md:h-6 mr-3 transition-transform duration-300 ${isHovered ? 'rotate-12' : ''}`} />
                  Start Sacred Conversation
                  <ArrowRight className={`w-5 h-5 md:w-6 md:h-6 ml-3 transition-transform duration-300 ${isHovered ? 'translate-x-1' : ''}`} />
                </Button>
                
                
              </div>
              
              <div className="mt-10 pt-8 border-t border-orange-200/50 dark:border-orange-700/30">
                <p className="text-xl md:text-2xl font-bold text-orange-600 dark:text-orange-400 mb-2">
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
        <div className="text-center mt-12 opacity-80">
          <p className="text-slate-600 dark:text-slate-400 italic">
            Made by Yashvanth S & Team
          </p>
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-orange-100/50 to-transparent dark:from-orange-950/30 pointer-events-none"></div>
    </div>
  );
}