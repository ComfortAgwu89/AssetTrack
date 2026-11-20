/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        navy: { 50: '#EEF2F8', 100: '#D6DFEE', 200: '#AEBFDD', 600: '#1B3A6B', 700: '#132E57', 800: '#0E2444', DEFAULT: '#0B1F3A', 900: '#0B1F3A' },
        teal: { 50: '#E7F6F5', 100: '#C6EAE8', 600: '#0E8F8B', 700: '#0B7571', DEFAULT: '#0E8F8B' },
        surface: '#F4F6F9',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
