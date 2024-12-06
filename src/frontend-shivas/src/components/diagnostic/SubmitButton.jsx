import React from "react"
import { Button } from "@mui/material"

export default function SubmitButton({ onClick }) {
  return (
    <Button
      variant="contained"
      onClick={onClick}
      style={{
        backgroundColor: "#00ffcc",
        color: "#000",
        padding: "0.8rem 2rem",
        fontWeight: "bold",
      }}
    >
      Submit
    </Button>
  )
}
