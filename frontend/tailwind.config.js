/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // ── Background layers ──────────────────────────────────────
        bg:       '#080c14',   // page background
        surface:  '#0f1624',   // card / panel surface
        'surface-2': '#141e30',  // elevated card
        'border-dim': '#1e2d45', // subtle border

        // ── Brand accents ─────────────────────────────────────────
        'accent-cyan':  '#00d4ff',
        'accent-blue':  '#0088ff',
        'accent-purple': '#7c3aed',

        // ── Market signals ────────────────────────────────────────
        gain:  '#00ff88',
        'gain-dim': '#00cc6a',
        loss:  '#ff3366',
        'loss-dim': '#cc2952',
        neutral: '#f0a500',

        // ── Text ─────────────────────────────────────────────────
        'text-primary': '#e8edf5',
        'text-secondary': '#8fa4be',
        'text-muted': '#4a637a',
      },

      fontFamily: {
        sans:  ['Inter', 'system-ui', 'sans-serif'],
        mono:  ['"JetBrains Mono"', 'Consolas', 'monospace'],
      },

      fontSize: {
        'price': ['1.125rem', { lineHeight: '1.2', fontWeight: '600', letterSpacing: '-0.02em' }],
        'price-lg': ['1.5rem', { lineHeight: '1.1', fontWeight: '700', letterSpacing: '-0.03em' }],
        'price-xl': ['2rem',   { lineHeight: '1',   fontWeight: '700', letterSpacing: '-0.04em' }],
      },

      boxShadow: {
        'glow-cyan':   '0 0 20px rgba(0,212,255,0.25), 0 0 60px rgba(0,212,255,0.08)',
        'glow-gain':   '0 0 20px rgba(0,255,136,0.25)',
        'glow-loss':   '0 0 20px rgba(255,51,102,0.25)',
        'card':        '0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04)',
      },

      backgroundImage: {
        'dot-grid': `radial-gradient(circle, #1e2d45 1px, transparent 1px)`,
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },

      backgroundSize: {
        'dot-grid': '24px 24px',
      },

      animation: {
        'ticker': 'ticker 40s linear infinite',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-in': 'slideIn 0.2s ease-out',
      },

      keyframes: {
        ticker: {
          '0%':   { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        fadeIn: {
          '0%':   { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%':   { opacity: '0', transform: 'translateX(-8px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
      },
    },
  },
  plugins: [],
}
