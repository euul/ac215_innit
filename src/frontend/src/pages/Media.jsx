import React, { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import "../styles/styles.css"
import { Container, Typography, Grid, Card, CardContent } from "@mui/material"

function Media() {
  const [videos, setVideos] = useState([])
  const [articles, setArticles] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    // Fetch YouTube transcripts
    fetch("http://localhost:8000/transcripts")
      .then((response) => response.json())
      .then((data) => {
        setVideos(data.transcripts.slice(0, 5)) // Limit to 5 videos
      })
      .catch((error) =>
        console.error("Error fetching video transcripts:", error)
      )

    // Fetch articles
    fetch("http://localhost:8000/articles")
      .then((response) => response.json())
      .then((data) => {
        setArticles(data.articles.slice(0, 5)) // Limit to 5 articles
      })
      .catch((error) => console.error("Error fetching articles:", error))
  }, [])

  // Handle click for videos
  const handleVideoClick = (video) => {
    if (!video.video_id) {
      console.error("Video ID not found:", video)
      return
    }
    navigate(`/media/video/${video.video_id}`, { state: { video } })
  }

  // Handle click for articles
  const handleArticleClick = (article) => {
    if (!article.id) {
      console.error("Article ID not found:", article)
      return
    }
    navigate(`/media/article/${article.id}`, { state: { article } })
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
          Browse and select a video or article to explore.
        </Typography>

        <Grid container spacing={4} style={{ marginTop: "1rem" }}>
          {/* Articles (left) */}
          <Grid item xs={12} md={6}>
            <h3 style={{ color: "#ffcc00" }}>Articles</h3>
            {articles.map((article, index) => (
              <Card
                key={index}
                onClick={() => handleArticleClick(article)}
                style={{
                  cursor: "pointer",
                  background: "linear-gradient(135deg, #ff6600, #ffcc00)", // Neon gradient
                  color: "#fff",
                  borderRadius: "12px",
                  boxShadow: "0 8px 20px rgba(0, 0, 0, 0.4)", // Strong retro shadow
                  marginBottom: "1rem",
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
                    style={{
                      fontFamily: "Press Start 2P, cursive",
                      fontSize: "1rem",
                      textShadow: "1px 1px #000",
                    }}
                  >
                    {article.Title}
                  </Typography>
                </CardContent>
              </Card>
            ))}
          </Grid>

          {/* Videos (right) */}
          <Grid item xs={12} md={6}>
            <h3 style={{ color: "#ffcc00" }}>Videos</h3>
            {videos.map((video, index) => (
              <Card
                key={index}
                onClick={() => handleVideoClick(video)}
                style={{
                  cursor: "pointer",
                  background: "linear-gradient(135deg, #3333ff, #00f2fe)", // Neon gradient
                  color: "#fff",
                  borderRadius: "12px",
                  boxShadow: "0 8px 20px rgba(0, 0, 0, 0.4)", // Strong retro shadow
                  marginBottom: "1rem",
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
                    style={{
                      fontFamily: "Press Start 2P, cursive",
                      fontSize: "1rem",
                      textShadow: "1px 1px #000",
                    }}
                  >
                    {video.video_name}
                  </Typography>
                </CardContent>
              </Card>
            ))}
          </Grid>
        </Grid>
      </Container>
    </div>
  )
}

export default Media
