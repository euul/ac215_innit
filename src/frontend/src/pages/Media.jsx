// src/pages/Media.jsx
import React, { useEffect, useState } from "react"
import "../styles/styles.css"
import {
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Container,
  Grid,
  Divider,
} from "@mui/material"
import MediaPlayer from "../components/MediaPlayer"

function Media() {
  const [transcripts, setTranscripts] = useState([])
  const [selectedVideo, setSelectedVideo] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch the transcripts from the backend
    fetch("http://localhost:8000/transcripts")
      .then((response) => response.json())
      .then((data) => {
        setTranscripts(data.transcripts)
        setLoading(false)
      })
      .catch((error) => {
        console.error("Error fetching transcripts:", error)
        setLoading(false)
      })
  }, [])

  const handleVideoSelect = (video) => {
    const cleanVideoId = video.video_id.split("&")[0] // Remove anything after &
    console.log("Selected video (cleaned):", cleanVideoId)
    setSelectedVideo({ ...video, video_id: cleanVideoId })
  }

  return (
    <Container maxWidth="lg" style={{ marginTop: "2rem" }}>
      <Typography variant="h4" component="h2" align="center" gutterBottom>
        Media
      </Typography>
      <Divider style={{ marginBottom: "1rem" }} />
      <Typography variant="subtitle1" align="center" gutterBottom>
        Select a video to display.
      </Typography>
      {loading ? (
        <div style={{ textAlign: "center", marginTop: "2rem" }}>
          <CircularProgress />
        </div>
      ) : (
        <Grid container spacing={3}>
          {/* Left side: Video Player */}
          <Grid item xs={12} md={6}>
            <div style={{ textAlign: "center" }}>
              {selectedVideo ? (
                <>
                  <Typography variant="h6" gutterBottom>
                    {selectedVideo.video_name}
                  </Typography>
                  <MediaPlayer videoId={selectedVideo.video_id} />
                </>
              ) : (
                <Typography variant="body1">
                  Select a video to display.
                </Typography>
              )}
            </div>
          </Grid>

          {/* Right side: Video List */}
          <Grid item xs={12} md={6}>
            {transcripts.map((transcript, index) => (
              <Card
                key={index}
                variant="outlined"
                style={{
                  marginBottom: "1rem",
                  backgroundColor: "#f9f9f9",
                  cursor: "pointer",
                }}
                onClick={() => handleVideoSelect(transcript)}
              >
                <CardContent>
                  <Typography variant="h6" component="div">
                    {transcript.video_name}
                  </Typography>
                  <Typography color="textSecondary">
                    Label: {transcript.label}
                  </Typography>
                </CardContent>
              </Card>
            ))}
          </Grid>
        </Grid>
      )}
    </Container>
  )
}

export default Media
