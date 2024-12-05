import React from "react"
import { useLocation } from "react-router-dom"
import { Box, Typography, List, ListItem } from "@mui/material"

function ArticleDetail() {
  const location = useLocation()
  const { article } = location.state || {} // Retrieve the article from state

  if (!article) {
    return (
      <Typography
        variant="h5"
        style={{
          color: "#fff",
          textAlign: "center",
          marginTop: "3rem",
        }}
      >
        Article not found
      </Typography>
    )
  }

  return (
    <Box
      style={{
        marginTop: "3rem",
        color: "#fff",
        display: "flex",
        flexDirection: "column",
        alignItems: "center", // Center-align the content
        padding: "0 2rem", // Padding for spacing on the sides
        paddingBottom: "10rem",
      }}
    >
      {/* Fixed Title */}
      <h2
        style={{
          color: "#00ffcc", // Neon green for the title
          textShadow: "2px 2px #000", // Retro shadow
          marginBottom: "1.5rem",
          fontWeight: "bold",
          textAlign: "center",
          width: "100%", // Match the width of the text below
          maxWidth: "800px", // Limit the maximum width of the title
          paddingBottom: "1rem",
        }}
      >
        {article.Title}
      </h2>

      {/* Key Words Section */}
      <div
        style={{
          width: "100%",
          maxWidth: "800px", // Match the width of the article text
          textAlign: "left", // Left-align the heading and list
          marginBottom: "2rem",
        }}
      >
        <h3 style={{ color: "#ffcc00", paddingBottom: "1rem" }}>Key words:</h3>
        {/*
        <List
          style={{
            paddingLeft: "2rem", // Indent the list items
            fontSize: "1.2rem",
            lineHeight: "1.8", // Improve readability
          }}
        >
          {article.vocab.split("\n").map((line, index) => (
            <ListItem
              key={index}
              style={{
                padding: "0.2rem 0",
                color: "#e0e0e0", // Softer white for readability
              }}
            >
              {line}
            </ListItem>
          ))}
        </List>
        */}
      </div>

      {/* Scrollable Text */}
      <Box
        style={{
          maxHeight: "500px", // Limit the height of the scrollable area
          overflowY: "auto", // Enable vertical scrolling
          width: "100%",
          maxWidth: "800px", // Limit the width of the text
          padding: "2rem",
          backgroundColor: "#222", // Subtle background for the text
          borderRadius: "10px",
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.5)", // Add a soft shadow
        }}
      >
        {article.Text.split("\n").map((paragraph, index) => (
          <Typography
            key={index}
            variant="body1"
            style={{
              marginBottom: "1.5rem", // Add space between paragraphs
              textIndent: "2rem", // Indent the first line of each paragraph
              fontSize: "1.2rem",
              lineHeight: "1.8", // Improve readability
              textAlign: "justify", // Align text for clean edges
              color: "#e0e0e0", // Softer white for readability
            }}
          >
            {paragraph}
          </Typography>
        ))}
      </Box>
    </Box>
  )
}

export default ArticleDetail
