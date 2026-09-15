/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        command: {
          bg: '#070b19',
          card: '#0d1527',
          cardHover: '#131e38',
          border: '#1b2d4b',
          borderGlow: '#00e5ff',
          textMuted: '#6b8299',
          cyan: '#00f0ff',
          blue: '#1677ff',
          badgeRed: '#ff4d4f',
          badgeGold: '#fadb14'
        }
      },
      boxShadow: {
        'glow-cyan': '0 0 15px rgba(0, 240, 255, 0.25)',
        'glow-blue': '0 0 15px rgba(22, 119, 255, 0.25)',
        'card-inset': 'inset 0 1px 0 0 rgba(255, 255, 255, 0.05)'
      }
    },
  },
  plugins: [],
}
