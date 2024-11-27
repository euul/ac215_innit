import React from "react"

function Footer() {
  const userLevel = "B2" // Placeholder for user level
  const progress = 75 // Example progress value

  return (
    <footer
      style={{
        position: "fixed", // Keeps it fixed to the screen
        bottom: 0,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        backgroundColor: "#333",
        color: "#fff",
        padding: "2rem 2rem",
        borderTop: "4px solid #00ffcc",
        fontFamily: "Press Start 2P",
        zIndex: 1000, // Ensures it's above other elements
      }}
    >
      {/* User Level */}
      <div style={{ fontSize: "1.2rem" }}>
        Level: <span style={{ color: "#00ffcc" }}>{userLevel}</span>
      </div>

      {/* Progress Bar */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          width: "25%",
        }}
      >
        <div
          style={{
            height: "20px",
            width: "100%",
            backgroundColor: "#555",
            border: "2px solid #000",
            borderRadius: "10px",
            overflow: "hidden",
            position: "relative",
          }}
        >
          <div
            style={{
              height: "100%",
              width: `${progress}%`,
              backgroundColor: "#00ffcc",
              transition: "width 0.5s ease",
              clipPath: "polygon(0% 0%, 100% 0%, 95% 100%, 0% 100%)", // Slanted edge
            }}
          ></div>
        </div>
        <span
          style={{
            marginLeft: "10px",
            fontSize: "1.2rem",
            color: "#00ffcc",
          }}
        >
          {progress}
        </span>
        <span
          style={{
            marginLeft: "10px",
            fontSize: "1.2rem",
            color: "#ffcc00",
          }}
        >
          /100
        </span>
      </div>
    </footer>
  )
}

export default Footer
