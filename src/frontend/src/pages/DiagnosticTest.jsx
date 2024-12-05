import React, { useEffect, useState } from "react"
import "../styles/styles.css"
import {
  Container,
  Typography,
  Grid,
  RadioGroup,
  FormControlLabel,
  Radio,
  Button,
} from "@mui/material"

function Diagnostic() {
  const [questions, setQuestions] = useState([])
  const [responses, setResponses] = useState({})
  const [submitted, setSubmitted] = useState(false)

  useEffect(() => {
    // Fetch the diagnostic test questions from the backend
    fetch("http://localhost:8000/diagnostic-test")
      .then((response) => response.json())
      .then((data) => {
        setQuestions(data.questions)
      })
      .catch((error) => console.error("Error fetching questions:", error))
  }, [])

  const handleAnswerChange = (questionIndex, selectedAnswer) => {
    setResponses((prev) => ({
      ...prev,
      [questionIndex]: selectedAnswer,
    }))
  }

  const handleSubmit = () => {
    if (Object.keys(responses).length < questions.length) {
      alert("Please answer all questions before submitting!")
      return
    }
    setSubmitted(true)
    console.log("User responses:", responses)
    // Optionally, send the responses to the backend
  }

  return (
    <div
      style={{
        backgroundColor: "#1a1a1a",
        minHeight: "100vh",
        padding: "2rem 0",
        paddingBottom: "160px",
        color: "#00ffcc", // Neon green text
        fontFamily: "Press Start 2P, cursive",
      }}
    >
      <Container maxWidth="md">
        <h2
          align="center"
          style={{
            color: "#00ffcc", // Neon green title
            textShadow: "2px 2px #000", // Retro shadow
            fontSize: "2.5rem",
          }}
        >
          Diagnostic Test
        </h2>
        <Typography
          variant="subtitle1"
          align="center"
          gutterBottom
          style={{
            color: "#fff", // White text
            textShadow: "1px 1px #000",
            fontSize: "1.2rem",
            paddingBottom: "5rem",
          }}
        >
          Complete the following 10 questions to get your language level. Good
          luck!
        </Typography>
        {!submitted ? (
          <Grid container spacing={4} justifyContent="center">
            {questions.map((question, index) => (
              <Grid
                item
                xs={12}
                md={6}
                key={index}
                style={{
                  marginLeft: "auto", // Pushes content closer to the center
                  marginRight: "auto",
                }}
              >
                <div style={{ marginBottom: "1.5rem", paddingLeft: "2rem" }}>
                  <Typography
                    variant="h6"
                    style={{
                      textShadow: "1px 1px #000",
                      marginBottom: "1rem",
                    }}
                  >
                    {index + 1}. {question.question}
                  </Typography>
                  <RadioGroup
                    value={responses[index] || ""}
                    onChange={(e) => handleAnswerChange(index, e.target.value)}
                  >
                    {question.choices.map((choice, choiceIndex) => (
                      <FormControlLabel
                        key={choiceIndex}
                        value={String.fromCharCode(65 + choiceIndex)} // Convert index to A, B, C, etc.
                        control={
                          <Radio
                            sx={{
                              color: "#fff", // White circle when unchecked
                              "&.Mui-checked": {
                                color: "#00ffcc", // Neon green when checked
                              },
                            }}
                          />
                        }
                        label={choice}
                        style={{
                          color: "#fff",
                          margin: "0.5rem 0",
                        }}
                      />
                    ))}
                  </RadioGroup>
                </div>
              </Grid>
            ))}
            <Grid item xs={12} style={{ textAlign: "center" }}>
              <Button
                variant="contained"
                style={{
                  backgroundColor: "#00ffcc",
                  color: "#000",
                  fontWeight: "bold",
                  fontFamily: "Press Start 2P, cursive",
                  padding: "0.8rem 2rem",
                  borderRadius: "20px",
                  boxShadow: "0 4px 10px rgba(0, 0, 0, 0.5)",
                  marginBottom: "2rem",
                }}
                onClick={handleSubmit}
              >
                Submit
              </Button>
            </Grid>
          </Grid>
        ) : (
          <Typography align="center" style={{ fontSize: "1.5rem" }}>
            Thank you for completing the test! Results will be processed.
          </Typography>
        )}
      </Container>
    </div>
  )
}

export default Diagnostic
