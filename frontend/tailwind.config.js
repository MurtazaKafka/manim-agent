/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        claude: {
          bg: '#faf9f7',
          bgDark: '#2d2d2d',
          text: '#3d3d3d',
          textLight: '#666666',
          primary: '#d97757',
          secondary: '#70b8d3',
          border: '#e5e5e5',
          borderDark: '#404040',
        },
      },
      animation: {
        'thinking': 'thinking 1.5s ease-in-out infinite',
      },
      keyframes: {
        thinking: {
          '0%, 100%': { opacity: '0.3' },
          '50%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};