/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        ff: {
          primary:   '#138A4B',
          dark:      '#075C35',
          deep:      '#06452B',
          light:     '#E9F7EF',
          soft:      '#F3FAF5',
          accent:    '#20A65A',
          bg:        '#F8FAF8',
          border:    '#E2E9E4',
          text:      '#17231D',
          secondary: '#65736B',
          muted:     '#9BAA9E',
        },
        brand: {
          50:  '#F3FAF5',
          100: '#E9F7EF',
          200: '#C5E8D3',
          300: '#8FD0AB',
          400: '#4DAF7C',
          500: '#20A65A',
          600: '#138A4B',
          700: '#075C35',
          800: '#06452B',
          900: '#022E1B',
        },
        earth: {
          50:  '#FFF7E1',
          100: '#FEEFC1',
          200: '#FDD97A',
          300: '#F8C040',
          400: '#F0B428',
          500: '#D89B18',
          600: '#B07A10',
          700: '#8A5D0C',
          800: '#664510',
          900: '#4A3110',
        },
        soil: {
          light: '#C4956B',
          medium: '#8B5E3C',
          dark: '#5C3317',
        }
      },
      borderRadius: {
        'ff':    '20px',
        'ff-sm': '12px',
        'ff-lg': '28px',
      },
      boxShadow: {
        'ff-sm': '0 2px 10px rgba(20, 50, 30, 0.06)',
        'ff':    '0 4px 20px rgba(20, 50, 30, 0.08)',
        'ff-lg': '0 8px 30px rgba(20, 50, 30, 0.10)',
        'ff-hover': '0 12px 40px rgba(20, 50, 30, 0.12)',
        'ff-green': '0 4px 20px rgba(19, 138, 75, 0.20)',
      },
      animation: {
        'fade-in':   'fadeIn 0.5s ease-out forwards',
        'fade-in-up':'fadeInUp 0.6s ease-out forwards',
        'score':     'scoreCount 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
        'float':     'floatUp 3s ease-in-out infinite',
        'leaf-pulse':'leafPulse 1.8s ease-in-out infinite',
        'pulse-soft':'pulse 2s ease-in-out infinite',
        'grow-bar':  'growBar 1s ease-out forwards',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeInUp: {
          '0%':   { opacity: '0', transform: 'translateY(24px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scoreCount: {
          '0%':   { opacity: '0', transform: 'scale(0.8)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        floatUp: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        leafPulse: {
          '0%, 100%': { transform: 'scale(1) rotate(-5deg)', opacity: '0.9' },
          '50%': { transform: 'scale(1.1) rotate(5deg)', opacity: '1' },
        },
        growBar: {
          '0%': { width: '0' },
        },
      },
    },
  },
  plugins: [],
}
