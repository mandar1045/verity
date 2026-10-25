/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#f7f6f2",
        surface: { DEFAULT: "#ffffff", 2: "#fbfaf7", 3: "#f2f1ec" },
        line: { DEFAULT: "#e5e3dc", strong: "#d3d0c6" },
        ink: { DEFAULT: "#16181d", 2: "#424854", 3: "#6b7180", 4: "#9298a4" },
        brand: {
          50: "#eef3fa", 100: "#dce6f4", 200: "#b9cde9", 300: "#86a8d8", 500: "#2c5ea8",
          600: "#22519a", 700: "#1a4480", 800: "#163a6c", 900: "#102a4f",
        },
        safe: { 50: "#ecf7ef", 100: "#d3eedb", 300: "#8fd0a4", 600: "#1f8a46", 700: "#16703a", 800: "#125c30" },
        warn: { 50: "#fff7e6", 100: "#feecc2", 300: "#f6c662", 600: "#c27c00", 700: "#9a5f00", 800: "#7a4b00" },
        danger: { 50: "#fdeeec", 100: "#fbd9d5", 300: "#ef9a90", 600: "#cc3a2e", 700: "#ae2a20", 800: "#8f2219" },
      },
      fontFamily: {
        sans: ["Inter", "Noto Sans Devanagari", "Noto Sans Tamil", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
        serif: ['"Source Serif 4"', "Noto Sans Devanagari", "Noto Sans Tamil", "Georgia", "serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(16, 24, 40, 0.04), 0 1px 3px rgba(16, 24, 40, 0.03)",
        pop: "0 12px 32px -8px rgba(16, 24, 40, 0.18), 0 4px 8px -4px rgba(16, 24, 40, 0.08)",
      },
      maxWidth: { page: "72rem" },
    },
  },
  plugins: [],
};
