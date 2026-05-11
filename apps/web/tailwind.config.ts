import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#1B3A6B",
          light:   "#E8EEF7",
          dark:    "#152d57",
        },
      },
    },
  },
  plugins: [],
}

export default config
