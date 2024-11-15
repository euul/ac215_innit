// src/components/Header.jsx
import React from "react"
import { Link } from "react-router-dom"
import { AppBar, Toolbar, Typography, Button, Container } from "@mui/material"

function Header() {
  return (
    <AppBar position="static" style={{ backgroundColor: "#333" }}>
      <Container maxWidth="md">
        <Toolbar>
          <Typography variant="h6" component="div" style={{ flexGrow: 1 }}>
            innit
          </Typography>
          <Button color="inherit" component={Link} to="/">
            Home
          </Button>
          <Button color="inherit" component={Link} to="/diagnostic">
            Diagnostic Test
          </Button>
          <Button color="inherit" component={Link} to="/media">
            Media
          </Button>
        </Toolbar>
      </Container>
    </AppBar>
  )
}

export default Header
