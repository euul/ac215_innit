// src/components/Sidebar.js
import React from "react"

function Sidebar({ onGenerateSummary, onGenerateQA }) {
  return (
    <aside
      style={{ padding: "1rem", backgroundColor: "#f5f5f5", width: "200px" }}
    >
      <h3>Actions</h3>
      <button
        onClick={onGenerateSummary}
        style={{ display: "block", margin: "0.5rem 0" }}
      >
        Generate Summary
      </button>
      <button
        onClick={onGenerateQA}
        style={{ display: "block", margin: "0.5rem 0" }}
      >
        Generate Q&A
      </button>
    </aside>
  )
}

export default Sidebar
