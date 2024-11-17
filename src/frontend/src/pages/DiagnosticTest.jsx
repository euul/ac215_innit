import React from "react"

function DiagnosticTest() {
  return (
    <div
      style={{
        textAlign: "center",
        marginTop: "2rem",
        backgroundColor: "#fafafa", // Light background color
        height: "calc(100vh - 100px)", // Full height minus header
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: "1rem",
      }}
    >
      <h2
        style={{
          fontFamily: "Pixel, sans-serif",
          color: "#555",
          fontSize: "2.5rem",
        }}
      >
        Diagnostic Test
      </h2>
      <p
        style={{
          fontFamily: "Pixel, sans-serif",
          color: "#777",
          fontSize: "1.2rem",
        }}
      >
        Take this test to determine your language level.
      </p>
      <button
        style={{
          backgroundColor: "#333",
          color: "#fff",
          border: "2px solid #000",
          padding: "1rem 2rem",
          fontSize: "1.2rem",
          fontFamily: "Pixel, sans-serif",
          cursor: "pointer",
          borderRadius: "10px",
          marginTop: "1rem",
        }}
      >
        Start Test
      </button>
    </div>
  )
}

export default DiagnosticTest
