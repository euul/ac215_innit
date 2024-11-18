import React, { useState, useEffect, useRef } from "react"
import { useLocation } from "react-router-dom"
import MediaPlayer from "../components/MediaPlayer"
import "../styles/styles.css"
import { Container, Grid, Typography, Box } from "@mui/material"

function MediaDetail() {
  const location = useLocation()
  const { video } = location.state || {}
  const [currentTime, setCurrentTime] = useState(0)
  const transcriptRef = useRef(null)

  if (!video) {
    return <Typography variant="h5">Video not found</Typography>
  }

  // Function to scroll the transcript into view
  const scrollToCurrentEntry = (index) => {
    const transcriptElement = transcriptRef.current
    const entryElement =
      transcriptElement.querySelectorAll(".transcript-entry")[index]
    if (entryElement) {
      entryElement.scrollIntoView({ behavior: "smooth", block: "center" })
    }
  }

  // Highlight the current transcript entry
  const getCurrentEntryIndex = () => {
    for (let i = 0; i < video.transcript.length; i++) {
      const startTime = parseFloat(video.transcript[i].start.replace(/:/g, ""))
      const nextStartTime =
        i + 1 < video.transcript.length
          ? parseFloat(video.transcript[i + 1].start.replace(/:/g, ""))
          : Infinity

      if (currentTime >= startTime && currentTime < nextStartTime) {
        return i
      }
    }
    return -1
  }

  const currentIndex = getCurrentEntryIndex()

  useEffect(() => {
    if (currentIndex !== -1) {
      scrollToCurrentEntry(currentIndex)
    }
  }, [currentIndex])

  return (
    <Container maxWidth="lg" style={{ marginTop: "2rem" }}>
      <Typography variant="h4" component="h2" align="center" gutterBottom>
        {video.video_name}
      </Typography>
      <Grid container spacing={4}>
        {/* Left: Video Player */}
        <Grid item xs={12} md={6}>
          <Box>
            <MediaPlayer
              videoId={video.video_id}
              onTimeUpdate={setCurrentTime}
            />
          </Box>
        </Grid>
        {/* Right: Transcript */}
        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom>
            Transcript
          </Typography>
          <div
            ref={transcriptRef}
            style={{ maxHeight: "400px", overflowY: "scroll" }}
          >
            {video.transcript.map((entry, index) => (
              <div
                key={index}
                className={`transcript-entry ${
                  index === currentIndex ? "active" : ""
                }`}
                style={{
                  padding: "1rem",
                  backgroundColor:
                    index === currentIndex ? "#d0f0fd" : "transparent",
                  borderRadius: "5px",
                }}
              >
                <Typography variant="body2">
                  <strong>Text:</strong> {entry.text}
                  <br />
                  <strong>Start:</strong> {entry.start}
                </Typography>
              </div>
            ))}
          </div>
        </Grid>
      </Grid>
    </Container>
  )
}

export default MediaDetail
