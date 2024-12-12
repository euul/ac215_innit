/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/app/**/*.{js,jsx}", "./src/components/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Source Sans Pro", "sans-serif"],
        montserrat: ["Montserrat", "sans-serif"],
        playfair: ["Playfair Display", "serif"],
        retro: ["'Press Start 2P'", "monospace"], // Add retro font
      },
      colors: {
        retroBlack: "#03120E", // Background color
        retroGreen: "#00FF00", // Neon green for text
        retroYellow: "#2D3047", // Bright yellow for headings
        retroPink: "#FF00FF", // Neon pink for links and accents
        retroBlue: "#0000FF", // Neon blue for buttons
        retroGray: "#222222", // Dark gray for patterns or cards
        Black: "#000",
      },
      backgroundImage: {
        retroPattern: `repeating-linear-gradient(
          45deg,
          #222222,
          #222222 10px,
          #333333 10px,
          #333333 20px
        )`, // Add retro diagonal stripe pattern
      },
      animation: {
        blink: "blink 1s infinite", // Blinking animation
      },
      keyframes: {
        blink: {
          "50%": { opacity: "0" }, // Keyframe for blinking effect
        },
      },
      textShadow: {
        // Add glowing text shadow effects
        green: "0 0 8px #00FF00, 0 0 12px #00FF00",
        pink: "0 0 8px #FF00FF, 0 0 12px #FF00FF",
        yellow: "0 0 8px #FFFF00, 0 0 12px #FFFF00",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
}
