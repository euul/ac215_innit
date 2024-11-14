// src/components/MainContent.js
import React from "react"

function MediaPlayer({ content }) {
  return (
    <main style={{ padding: "1rem", flexGrow: 1 }}>
      <h2>Media Display</h2>
      <div style={{ marginTop: "1rem" }}>
        {content ? (
          <p>{content}</p>
        ) : (
          <p>Select an article or media to display.</p>
        )}
      </div>
    </main>
  )
}

export default MediaPlayer
