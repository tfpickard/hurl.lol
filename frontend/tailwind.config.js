/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './contexts/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Synthwave Night Mode Colors
        'synth-dark': '#0A0E27',
        'synth-darker': '#050711',
        'synth-surface': '#1a1a2e',
        'synth-pink': '#FF006E',
        'synth-cyan': '#00F0FF',
        'synth-purple': '#8B00FF',
        'synth-yellow': '#FFD700',
        'synth-magenta': '#FF10F0',

        // Synthwave Day Mode Colors
        'synth-light': '#E8DFF5',
        'synth-lighter': '#F5F0FF',
        'synth-light-surface': '#FFF',
        'synth-pink-day': '#C7006B',
        'synth-cyan-day': '#00B8CC',
        'synth-purple-day': '#6B00CC',
        'synth-yellow-day': '#CC9900',
        'synth-magenta-day': '#CC00BB',
      },
      boxShadow: {
        'neon-pink': '0 0 5px theme("colors.synth-pink"), 0 0 20px theme("colors.synth-pink")',
        'neon-cyan': '0 0 5px theme("colors.synth-cyan"), 0 0 20px theme("colors.synth-cyan")',
        'neon-purple': '0 0 5px theme("colors.synth-purple"), 0 0 20px theme("colors.synth-purple")',
        'neon-pink-strong': '0 0 10px theme("colors.synth-pink"), 0 0 40px theme("colors.synth-pink"), 0 0 80px theme("colors.synth-pink")',
        'neon-cyan-strong': '0 0 10px theme("colors.synth-cyan"), 0 0 40px theme("colors.synth-cyan"), 0 0 80px theme("colors.synth-cyan")',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'scan-line': 'scan-line 8s linear infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
        'scan-line': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
      },
    },
  },
  plugins: [],
}
