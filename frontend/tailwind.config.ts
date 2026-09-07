import type { Config } from "tailwindcss";

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "pitch-black": "#000000",
        obsidian: {
          50: "#050505",
          100: "#0A0A0A",
          150: "#0F0F12",
          200: "#141418",
          300: "#1C1C22",
          400: "#27272F",
          500: "#3F3F46",
        },
        crimson: {
          300: "#FDA4AF",
          400: "#FB7185",
          500: "#F43F5E",
          600: "#E11D48",
          700: "#BE123C",
          800: "#9F1239",
          900: "#881337",
          950: "#4C0519",
        },
        ruby: {
          neon: "#FF1A55",
          vivid: "#DC2626",
          dark: "#991B1B",
          deep: "#450A0A",
        },
      },
      boxShadow: {
        "crimson-sm": "0 0 15px rgba(225, 29, 72, 0.25)",
        "crimson-md": "0 0 25px rgba(225, 29, 72, 0.4)",
        "crimson-lg": "0 0 40px rgba(225, 29, 72, 0.6)",
        "crimson-laser": "0 0 8px #FF1A55, 0 0 20px rgba(225, 29, 72, 0.5)",
      },
      animation: {
        "border-beam": "border-beam 6s linear infinite",
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "shimmer": "shimmer 2.5s linear infinite",
        "float": "float 3s ease-in-out infinite",
      },
      keyframes: {
        "border-beam": {
          "100%": {
            "offset-distance": "100%",
          },
        },
        shimmer: {
          from: {
            backgroundPosition: "0 0",
          },
          to: {
            backgroundPosition: "-200% 0",
          },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-4px)" },
        },
      },
      fontFamily: {
        sans: ["Outfit", "Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
} satisfies Config;
