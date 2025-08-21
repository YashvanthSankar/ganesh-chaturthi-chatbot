import type { Config } from "tailwindcss";

const config: Config = {
    darkMode: ["class"],
    content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
  	extend: {
  		colors: {
  			// Ganesha-inspired divine color palette
  			ganesha: {
  				saffron: '#FF9933',
  				gold: '#FFD700', 
  				copper: '#B87333',
  				vermillion: '#E34234',
  				lotus: '#DDA0DD',
  				sacred: '#8B0000',
  				divine: '#4B0082',
  				blessing: '#FF6347',
  				peace: '#F0E68C',
  				wisdom: '#DAA520'
  			},
  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			}
  		},
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
  		animation: {
  			"float": "float 3s ease-in-out infinite",
  			"glow": "glow 2s ease-in-out infinite alternate",
  			"pulse-glow": "pulse-glow 1.5s ease-in-out infinite",
  			"shake": "shake 0.5s ease-in-out",
  			"divine-pulse": "divine-pulse 2s ease-in-out infinite",
  		},
  		keyframes: {
  			float: {
  				"0%, 100%": { transform: "translateY(0px)" },
  				"50%": { transform: "translateY(-10px)" },
  			},
  			glow: {
  				"0%": { boxShadow: "0 0 5px #FFD700, 0 0 10px #FFD700, 0 0 15px #FFD700" },
  				"100%": { boxShadow: "0 0 10px #FFD700, 0 0 20px #FFD700, 0 0 30px #FFD700" },
  			},
  			"pulse-glow": {
  				"0%, 100%": { 
  					boxShadow: "0 0 5px rgba(255, 215, 0, 0.5)",
  					transform: "scale(1)"
  				},
  				"50%": { 
  					boxShadow: "0 0 20px rgba(255, 215, 0, 0.8)",
  					transform: "scale(1.05)"
  				},
  			},
  			shake: {
  				"0%, 100%": { transform: "translateX(0)" },
  				"25%": { transform: "translateX(-5px)" },
  				"75%": { transform: "translateX(5px)" },
  			},
  			"divine-pulse": {
  				"0%, 100%": { 
  					opacity: "0.8",
  					transform: "scale(1)"
  				},
  				"50%": { 
  					opacity: "1",
  					transform: "scale(1.02)"
  				},
  			},
  		},
  		fontFamily: {
  			devanagari: ["Noto Sans Devanagari", "sans-serif"],
  		},
  	}
  },
  plugins: [require("tailwindcss-animate")],
};
export default config;
