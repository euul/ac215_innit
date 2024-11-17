import React from "react"
import { useLocation } from "react-router-dom"
import MediaPlayer from "../components/MediaPlayer"
import "../styles/styles.css"
import { Container, Grid, Typography, Box } from "@mui/material"

function MediaDetail() {
  const location = useLocation()
  const { video } = location.state || {}

  if (!video) {
    return <Typography variant="h5">Video not found</Typography>
  }

  return (
    <Container maxWidth="lg" style={{ marginTop: "2rem" }}>
      <Typography variant="h4" component="h2" align="center" gutterBottom>
        {video.video_name}
      </Typography>
      <Grid container spacing={4}>
        {/* Left: Video Player */}
        <Grid item xs={12} md={6}>
          <Box>
            <MediaPlayer videoId={video.video_id} />
          </Box>
        </Grid>
        {/* Right: Transcript */}
        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom>
            Transcript
          </Typography>
          {video.transcript.map((entry, index) => (
            <Typography
              key={index}
              variant="body2"
              style={{ marginBottom: "1rem" }}
            >
              <strong>Text:</strong> {entry.text}
              <br />
              <strong>Start:</strong> {entry.start} <strong>Duration:</strong>{" "}
              {entry.duration}s
            </Typography>
          ))}
        </Grid>
      </Grid>
    </Container>
  )
}

export default MediaDetail
