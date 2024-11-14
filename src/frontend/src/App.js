// src/App.js
import React, { useState } from "react"
import Header from "./components/Header"
import MediaPlayer from "./components/MediaPlayer"
import Sidebar from "./components/Sidebar"

function App() {
  const [content, setContent] = useState(
    "This is a sample article or media content."
  )

  const generateSummary = () => {
    alert("Summary generated!")
  }

  const generateQA = () => {
    alert("Q&A generated!")
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <Header />
      <div style={{ display: "flex", flex: 1 }}>
        <Sidebar
          onGenerateSummary={generateSummary}
          onGenerateQA={generateQA}
        />
        <MediaPlayer content={content} />
      </div>
    </div>
  )
}

export default App
