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

function Media() {
  const [transcripts, setTranscripts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
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

  return (
    <Container maxWidth="md" style={{ marginTop: "2rem" }}>
      <Typography variant="h4" component="h2" align="center" gutterBottom>
        Media
      </Typography>
      <Divider style={{ marginBottom: "1rem" }} />
      <Typography variant="subtitle1" align="center" gutterBottom>
        Browse video transcripts at your language level.
      </Typography>
      {loading ? (
        <div style={{ textAlign: "center", marginTop: "2rem" }}>
          <CircularProgress />
        </div>
      ) : (
        <Grid container spacing={3}>
          {transcripts.length > 0 ? (
            transcripts.map((transcript, index) => (
              <Grid item xs={12} key={index}>
                <Card
                  variant="outlined"
                  style={{
                    marginBottom: "1rem",
                    backgroundColor: "#f9f9f9",
                  }}
                >
                  <CardContent>
                    <Typography variant="h5" component="div">
                      {transcript.video_name}
                    </Typography>
                    <Typography color="textSecondary">
                      Video ID: {transcript.video_id}
                    </Typography>
                    <Typography variant="subtitle1" gutterBottom>
                      Transcript:
                    </Typography>
                    {transcript.transcript.map((entry, entryIndex) => (
                      <Typography
                        key={entryIndex}
                        variant="body2"
                        color="textSecondary"
                        paragraph
                        style={{
                          margin: "0.5rem 0",
                          borderLeft: "3px solid #3f51b5",
                          paddingLeft: "0.5rem",
                        }}
                      >
                        <strong>Text:</strong> {entry.text}
                        <br />
                        <strong>Start:</strong> {entry.start}{" "}
                        <strong>Duration:</strong> {entry.duration}s
                      </Typography>
                    ))}
                  </CardContent>
                </Card>
              </Grid>
            ))
          ) : (
            <Typography variant="body1" align="center">
              No transcripts available.
            </Typography>
          )}
        </Grid>
      )}
    </Container>
  )
}

export default Media
