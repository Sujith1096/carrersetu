/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          50: '#F2F7F4',
          100: '#E1ECE6',
          200: '#C2D9CD',
          300: '#9EBEAF',
          400: '#5C917B',
          500: '#2A6650',
          600: '#1E4F3E',
          700: '#174133',
          800: '#123C2E', // Brand Primary
          900: '#0B261D',
          950: '#071812',
        },
        gold: {
          50: '#FDFBF4',
          100: '#F9F4E4',
          200: '#F1E6C1',
          300: '#E6D397',
          400: '#DABF6E',
          500: '#D4AF37', // Brand Gold
          600: '#C5A059',
          700: '#A37D24',
          800: '#81611B',
          900: '#5F4613',
        },
        ivory: {
          50: '#FCFDFC',
          100: '#F8FAF8',
          200: '#F3F6F4',
          300: '#E9EFEA',
          400: '#D6E0D8',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
        serif: ['Playfair Display', 'Merriweather', 'serif'],
      },
      boxShadow: {
        'premium': '0 10px 30px -10px rgba(18, 60, 46, 0.08), 0 4px 6px -2px rgba(18, 60, 46, 0.03)',
        'premium-lg': '0 20px 40px -15px rgba(18, 60, 46, 0.12), 0 0 0 1px rgba(18, 60, 46, 0.04)',
        'gold-glow': '0 0 25px -5px rgba(212, 175, 55, 0.25)',
      }
    },
  },
  plugins: [],
}
