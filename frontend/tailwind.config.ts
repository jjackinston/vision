import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: { DEFAULT: "hsl(var(--card))", foreground: "hsl(var(--card-foreground))" },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        primary: { DEFAULT: "hsl(var(--primary))", foreground: "hsl(var(--primary-foreground))" },
        muted: { DEFAULT: "hsl(var(--muted))", foreground: "hsl(var(--muted-foreground))" },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      animation: {
        "fade-in":  "fadeIn 0.2s ease-out",
        "fade-out": "fadeOut 0.15s ease-in",
        "slide-up": "slideUp 0.3s ease-out",
        "sheet-in-left":    "sheetInLeft 0.25s cubic-bezier(0.32,0.72,0,1)",
        "sheet-out-left":   "sheetOutLeft 0.2s ease-in forwards",
        "sheet-in-right":   "sheetInRight 0.25s cubic-bezier(0.32,0.72,0,1)",
        "sheet-out-right":  "sheetOutRight 0.2s ease-in forwards",
        "sheet-in-bottom":  "sheetInBottom 0.25s cubic-bezier(0.32,0.72,0,1)",
        "sheet-out-bottom": "sheetOutBottom 0.2s ease-in forwards",
      },
      keyframes: {
        fadeIn:  { from: { opacity: "0" }, to:   { opacity: "1" } },
        fadeOut: { from: { opacity: "1" }, to:   { opacity: "0" } },
        slideUp: { from: { transform: "translateY(8px)", opacity: "0" }, to: { transform: "translateY(0)", opacity: "1" } },
        sheetInLeft:    { from: { transform: "translateX(-100%)" }, to: { transform: "translateX(0)" } },
        sheetOutLeft:   { from: { transform: "translateX(0)" },     to: { transform: "translateX(-100%)" } },
        sheetInRight:   { from: { transform: "translateX(100%)" },  to: { transform: "translateX(0)" } },
        sheetOutRight:  { from: { transform: "translateX(0)" },     to: { transform: "translateX(100%)" } },
        sheetInBottom:  { from: { transform: "translateY(100%)" },  to: { transform: "translateY(0)" } },
        sheetOutBottom: { from: { transform: "translateY(0)" },     to: { transform: "translateY(100%)" } },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
