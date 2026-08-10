/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['IBM Plex Sans', 'sans-serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      },
      fontSize: {
        // Boosted font sizes (+2px for text-xs, text-sm, text-base, etc.)
        'xs': ['0.875rem', { lineHeight: '1.35rem' }],   // 14px (+2px from 12px)
        'sm': ['1rem', { lineHeight: '1.5rem' }],        // 16px (+2px from 14px)
        'base': ['1.125rem', { lineHeight: '1.75rem' }], // 18px (+2px from 16px)
        'lg': ['1.25rem', { lineHeight: '1.85rem' }],    // 20px (+2px from 18px)
        'xl': ['1.375rem', { lineHeight: '2rem' }],      // 22px (+2px from 20px)
        '2xl': ['1.625rem', { lineHeight: '2.25rem' }],  // 26px
        '3xl': ['2rem', { lineHeight: '2.5rem' }],       // 32px
      },
      colors: {
        // User palette hex codes:
        // #2b6777 (Deep Teal)
        // #c8d8e4 (Ice Blue)
        // #ffffff (Pure White)
        // #f2f2f2 (Light Gray Surface)
        // #52ab98 (Vibrant Jade)
        teal: {
          50: '#f0f6f8',
          100: '#c8d8e4',
          200: '#9ebece',
          300: '#6d9eb0',
          400: '#488595',
          500: '#2b6777',  // Primary #2b6777
          600: '#22525f',
          700: '#1b424d',
          800: '#143038',
          900: '#0f172a',  // Dark Text #0f172a
          DEFAULT: '#2b6777',
        },
        jade: {
          50: '#edf8f5',
          100: '#d2ede6',
          200: '#a7dcd0',
          300: '#7bcbb9',
          400: '#52ab98',  // Accent #52ab98
          500: '#3e8f7e',
          600: '#307365',
          700: '#24574d',
          800: '#193c35',
          900: '#0e221e',
          DEFAULT: '#52ab98',
        },
        ice: {
          50: '#f7fafc',
          100: '#eef4f8',
          200: '#c8d8e4',  // Light Blue #c8d8e4
          300: '#a3bed3',
          400: '#7fa4c2',
          DEFAULT: '#c8d8e4',
        },
        surface: {
          bg: '#f2f2f2',   // Canvas #f2f2f2
          card: '#ffffff', // Card #ffffff
          alt: '#e8eff4',
          muted: '#dbe5ec',
          DEFAULT: '#f2f2f2',
        },
        // Ultra-High Contrast Dark Text Tokens
        darktext: {
          primary: '#0f172a',
          secondary: '#1e293b',
          muted: '#334155',
        },
        // Slate mapping tuned for 100% text legibility
        slate: {
          50: '#ffffff',
          100: '#f8fafc',
          200: '#f1f5f9',
          300: '#e2e8f0',
          400: '#475569',  // Dark Gray Muted Text (Contrast > 7:1)
          500: '#334155',  // Solid Slate Text (Contrast > 10:1)
          600: '#1e293b',  // Deep Charcoal Body Text (Contrast > 14:1)
          700: '#0f172a',  // Black Title Text (Contrast > 17:1)
          800: '#0f172a',  // Black Heading Text
          850: '#0f172a',  // Ultra Black Heading Text
          900: '#ffffff',  // Card background
          950: '#f2f2f2',  // Page background
        }
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.35rem',
        '3xl': '1.85rem',
        '4xl': '2.25rem',
        'full': '9999px',
      },
      boxShadow: {
        'soft': '0 10px 30px -5px rgba(15, 23, 42, 0.06), 0 4px 12px -2px rgba(15, 23, 42, 0.03)',
        'soft-lg': '0 20px 40px -10px rgba(15, 23, 42, 0.10), 0 8px 20px -4px rgba(15, 23, 42, 0.05)',
        'jade-glow': '0 4px 16px 0 rgba(82, 171, 152, 0.35)',
        'teal-glow': '0 4px 16px 0 rgba(43, 103, 119, 0.30)',
      }
    },
  },
  plugins: [],
}
