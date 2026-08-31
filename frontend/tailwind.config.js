/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        void: "#05070a",
        panel: "#0b0f16",
        panelBorder: "#1c2531",
        accent: "#22d3ee",
        accentDim: "#0e7490",
        danger: "#f43f5e",
        warn: "#f59e0b",
        safe: "#34d399",
        muted: "#64748b",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      boxShadow: {
        glow: "0 0 40px -8px rgba(34, 211, 238, 0.35)",
      },
      backgroundImage: {
        grid: "linear-gradient(to right, rgba(148,163,184,0.06) 1px, transparent 1px), linear-gradient(to bottom, rgba(148,163,184,0.06) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "36px 36px",
      },
    },
  },
  plugins: [],
};
