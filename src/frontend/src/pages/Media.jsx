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
    <div
      style={{
        backgroundColor: "#1a1a1a", // Dark retro background
        minHeight: "100vh",
        padding: "2rem 0",
        color: "#00ffcc", // Neon green text
        fontFamily: "Press Start 2P, cursive", // Retro font
      }}
    >
      <Container maxWidth="lg" style={{ marginTop: "2rem" }}>
        <h2
          align="center"
          style={{
            color: "#00ffcc", // Neon green title
            textShadow: "2px 2px #000", // Retro shadow
            fontSize: "2.5rem",
          }}
        >
          Media
        </h2>
        <Typography
          variant="subtitle1"
          align="center"
          gutterBottom
          style={{
            color: "#fff", // White text
            textShadow: "1px 1px #000",
            fontSize: "1.2rem",
          }}
        >
          Browse and select a video to explore.
        </Typography>
        <Grid container spacing={4} style={{ marginTop: "2rem" }}>
          {transcripts.map((video, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card
                onClick={() => handleClick(video)}
                style={{
                  cursor: "pointer",
                  background: "linear-gradient(135deg, #3333ff, #00f2fe)", // Neon gradient
                  color: "#fff",
                  borderRadius: "12px",
                  boxShadow: "0 8px 20px rgba(0, 0, 0, 0.4)", // Strong retro shadow
                  transition: "transform 0.3s ease",
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = "scale(1.05)" // Enlarge on hover
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = "scale(1)" // Reset scale
                }}
              >
                <CardContent>
                  <Typography
                    variant="h6"
                    component="div"
                    gutterBottom
                    style={{
                      fontFamily: "Press Start 2P, cursive", // Retro font
                      fontSize: "1rem",
                      textShadow: "1px 1px #000", // Retro shadow
                    }}
                  >
                    {video.video_name}
                  </Typography>
                  <Typography
                    variant="body2"
                    style={{
                      fontFamily: "Press Start 2P, cursive",
                      fontSize: "0.8rem",
                      color: "#ffcc00", // Neon green for details
                    }}
                  >
                    Label: {video.label}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </div>
  )
}

export default Media
