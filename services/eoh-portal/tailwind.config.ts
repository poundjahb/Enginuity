import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./features/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        base: {
          950: "#040914",
          900: "#081126",
          800: "#0d1b39",
        },
        accent: {
          cyan: "#21d4fd",
          mint: "#17d9a3",
          amber: "#f9a826",
          red: "#ef4444",
        },
      },
      boxShadow: {
        card: "0 14px 30px rgba(1, 7, 20, 0.45)",
        glow: "0 0 0 1px rgba(33, 212, 253, 0.25), 0 18px 35px rgba(1, 7, 20, 0.5)",
      },
      backgroundImage: {
        "mesh-grid":
          "linear-gradient(rgba(45, 90, 145, 0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(45, 90, 145, 0.15) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "48px 48px",
      },
      fontFamily: {
        sans: ["Manrope", "Segoe UI", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
