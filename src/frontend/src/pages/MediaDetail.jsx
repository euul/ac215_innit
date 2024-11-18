import React, { useState, useEffect, useRef } from "react"
import { useLocation } from "react-router-dom"
import MediaPlayer from "../components/MediaPlayer"
import "../styles/styles.css"
import { Container, Grid, Typography, Box } from "@mui/material"

// Convert "hh:mm:ss" to seconds
function convertToSeconds(timeString) {
  const parts = timeString.split(":").map(Number)
  if (parts.length === 3) {
    const [hours, minutes, seconds] = parts
    return hours * 3600 + minutes * 60 + seconds
  } else if (parts.length === 2) {
    const [minutes, seconds] = parts
    return minutes * 60 + seconds
  }
  return parseFloat(timeString)
}

function MediaDetail() {
  const location = useLocation()
  const { video } = location.state || {}
  const [currentTime, setCurrentTime] = useState(0)
  const transcriptRef = useRef(null)

  if (!video) {
    return <Typography variant="h5">Video not found</Typography>
  }

  // Process the transcript into seconds
  const processedTranscript = video.transcript.map((entry) => ({
    ...entry,
    startInSeconds: convertToSeconds(entry.start),
  }))

  const getCurrentEntryIndex = () => {
    for (let i = 0; i < processedTranscript.length; i++) {
      const startTime = processedTranscript[i].startInSeconds
      const nextStartTime =
        i + 1 < processedTranscript.length
          ? processedTranscript[i + 1].startInSeconds
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
      const transcriptElement = transcriptRef.current
      const entryElement =
        transcriptElement.querySelectorAll(".transcript-entry")[currentIndex]
      if (entryElement) {
        entryElement.scrollIntoView({ behavior: "smooth", block: "center" })
      }
    }
  }, [currentIndex])

  return (
    <Container maxWidth="lg" style={{ marginTop: "2rem" }}>
      <Typography variant="h4" component="h2" align="center" gutterBottom>
        {video.video_name}
      </Typography>
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Box>
            <MediaPlayer
              videoId={video.video_id}
              onTimeUpdate={setCurrentTime}
            />
          </Box>
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom>
            Transcript
          </Typography>
          <div
            ref={transcriptRef}
            style={{ maxHeight: "400px", overflowY: "scroll" }}
          >
            {processedTranscript.map((entry, index) => (
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
