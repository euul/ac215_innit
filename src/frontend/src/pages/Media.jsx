import React, { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import "../styles/styles.css"
import { Container, Typography, Grid, Card, CardContent } from "@mui/material"

function Media() {
  const [transcripts, setTranscripts] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    // Fetch the transcripts from the backend
    fetch("http://localhost:8000/transcripts")
      .then((response) => response.json())
      .then((data) => {
        setTranscripts(data.transcripts)
      })
      .catch((error) => console.error("Error fetching transcripts:", error))
  }, [])

  const handleClick = (video) => {
    navigate(`/media/${video.video_id}`, { state: { video } })
  }

  return (
    <Container maxWidth="lg" style={{ marginTop: "2rem" }}>
      <Typography variant="h4" component="h2" align="center" gutterBottom>
        Media
      </Typography>
      <Typography variant="subtitle1" align="center" gutterBottom>
        Browse and select a video to explore.
      </Typography>
      <Grid container spacing={4} style={{ marginTop: "2rem" }}>
        {transcripts.map((video, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card
              onClick={() => handleClick(video)}
              style={{
                cursor: "pointer",
                background: "linear-gradient(135deg, #4facfe, #00f2fe)",
                color: "#fff",
                borderRadius: "12px",
                boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
              }}
            >
              <CardContent>
                <Typography variant="h6" component="div" gutterBottom>
                  {video.video_name}
                </Typography>
                <Typography variant="body2">Label: {video.label}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  )
}

export default Media
