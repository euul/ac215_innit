// src/components/MediaPlayer.jsx
import React from "react"
import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  Container,
} from "@mui/material"

function MediaPlayer({ content }) {
  return (
    <Container maxWidth="md" style={{ marginTop: "2rem" }}>
      <Typography variant="h4" align="center" gutterBottom>
        Media Display
      </Typography>
      {content ? (
        <Card
          style={{
            marginTop: "1rem",
            backgroundColor: "#f9f9f9",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
          }}
        >
          {content.type === "video" && content.videoUrl ? (
            <CardMedia
              component="iframe"
              src={content.videoUrl}
              title={content.title}
              style={{ height: "300px", marginBottom: "1rem" }}
            />
          ) : (
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {content.title || "No Title"}
              </Typography>
              <Typography variant="body1">
                {content.text || "No Content"}
              </Typography>
            </CardContent>
          )}
        </Card>
      ) : (
        <Typography variant="subtitle1" align="center" color="textSecondary">
          Select an article or media to display.
        </Typography>
      )}
    </Container>
  )
}

export default MediaPlayer
