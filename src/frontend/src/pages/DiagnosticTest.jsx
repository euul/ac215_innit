import React from "react"

function DiagnosticTest() {
  return (
    <div
      style={{
        textAlign: "center",
        marginTop: "2rem",
        backgroundColor: "#1a1a1a", // Dark background for retro feel
        height: "calc(100vh - 100px)", // Full height minus header
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: "1rem",
        color: "#00ffcc", // Neon green text
        fontFamily: "Press Start 2P, cursive", // Retro font
      }}
    >
      <h2
        style={{
          color: "#00ffcc", // Neon green
          fontSize: "2.5rem",
          textShadow: "2px 2px #000", // Retro shadow
        }}
      >
        Diagnostic Test
      </h2>
      <p
        style={{
          color: "#fff", // White text
          fontSize: "1.2rem",
          textShadow: "1px 1px #000", // Retro shadow
        }}
      >
        Take this test to determine your language level.
      </p>
      <button
        style={{
          backgroundColor: "#3333ff", // Bright blue button
          color: "#fff",
          border: "4px solid #ff00cc", // Neon pink border
          padding: "1rem 2rem",
          fontSize: "1rem",
          fontFamily: "Press Start 2P, cursive", // Retro font
          cursor: "pointer",
          borderRadius: "8px",
          marginTop: "1rem",
          textTransform: "uppercase",
          textShadow: "1px 1px #000", // Retro shadow
          transition: "transform 0.3s ease, background 0.3s ease",
          boxShadow: "0 5px 15px rgba(255, 0, 204, 0.6)", // Neon glow effect
        }}
        onMouseOver={(e) => {
          e.target.style.backgroundColor = "#ff00cc" // Change to neon pink on hover
          e.target.style.transform = "scale(1.1)" // Slightly enlarge
        }}
        onMouseOut={(e) => {
          e.target.style.backgroundColor = "#3333ff" // Revert to blue
          e.target.style.transform = "scale(1)" // Reset scale
        }}
      >
        Start Test
      </button>
    </div>
  )
}

export default DiagnosticTest
