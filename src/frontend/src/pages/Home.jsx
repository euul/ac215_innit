import React from "react"
import { Container, Typography } from "@mui/material"

function Home() {
  return (
    <Container maxWidth="md" style={{ textAlign: "center", marginTop: "2rem" }}>
      <Typography variant="h2" component="h2" gutterBottom>
        Welcome to the Language Learning App
      </Typography>
      <Typography variant="body1">
        Take a diagnostic test to find your level, or explore articles and
        videos suited to your level.
      </Typography>
    </Container>
  )
}

export default Home
