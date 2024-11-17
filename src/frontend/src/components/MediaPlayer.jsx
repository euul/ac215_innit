import React, { useEffect } from "react"

function MediaPlayer({ videoId }) {
  useEffect(() => {
    console.log("Loading YouTube Player for videoId:", videoId)
  }, [videoId])

  if (!videoId) {
    return (
      <div style={{ textAlign: "center", marginTop: "2rem" }}>
        <p>Select a video to display.</p>
      </div>
    )
  }

  // Ensure videoId is cleaned of any extra query parameters
  const cleanVideoId = videoId.split("&")[0] // Split by "&" and take the first part

  return (
    <div style={{ textAlign: "center", marginTop: "2rem" }}>
      <iframe
        width="100%"
        height="315"
        src={`https://www.youtube.com/embed/${cleanVideoId}`} // Use cleanVideoId here
        title="YouTube video player"
        frameBorder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
      ></iframe>
    </div>
  )
}

export default MediaPlayer
