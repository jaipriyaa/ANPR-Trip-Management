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
          600: '#235462',
          700: '#1b424d',
          800: '#143038',
          900: '#0f2931',  // High Contrast Text #0f2931
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
        // High Contrast Light Mode Text Colors
        darktext: {
          primary: '#0f2931',
          secondary: '#2b6777',
          muted: '#4d6e78',
        },
        // Seamless theme compatibility mapping for crisp light mode text & surfaces
        slate: {
          50: '#ffffff',
          100: '#f8fafc',
          200: '#e8eff4',
          300: '#c8d8e4',
          400: '#4d6e78',  // Muted readable text
          500: '#2b6777',  // Primary accent text
          600: '#235462',
          700: '#1a3e47',
          800: '#16353e',  // High contrast body text
          850: '#0f2931',  // Deep contrast title text
          900: '#ffffff',  // Cards background
          950: '#f2f2f2',  // Layout background
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
        'soft': '0 10px 30px -5px rgba(43, 103, 119, 0.08), 0 4px 12px -2px rgba(43, 103, 119, 0.04)',
        'soft-lg': '0 20px 40px -10px rgba(43, 103, 119, 0.12), 0 8px 20px -4px rgba(43, 103, 119, 0.06)',
        'jade-glow': '0 4px 16px 0 rgba(82, 171, 152, 0.35)',
        'teal-glow': '0 4px 16px 0 rgba(43, 103, 119, 0.30)',
      }
    },
  },
  plugins: [],
}
