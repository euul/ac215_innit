"use client"

import React, { useEffect, useState } from "react"
import QuestionCard from "@/components/diagnostic/QuestionCard"
import SubmitButton from "@/components/diagnostic/SubmitButton"
import styles from "./styles.module.css"
import DataService from "@/services/DataService" // Backend interaction

export default function DiagnosticTestPage() {
  const [questions, setQuestions] = useState([])
  const [responses, setResponses] = useState({})
  const [submitted, setSubmitted] = useState(false)

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const response = await DataService.GetDiagnosticTestQuestions()
        setQuestions(response.data.questions)
      } catch (error) {
        console.error("Error fetching questions:", error)
      }
    }
    fetchQuestions()
  }, [])

  const handleAnswerChange = (index, selectedAnswer) => {
    setResponses((prev) => ({
      ...prev,
      [index]: selectedAnswer,
    }))
  }

  const handleSubmit = async () => {
    if (Object.keys(responses).length < questions.length) {
      alert("Please answer all questions before submitting!")
      return
    }
    setSubmitted(true)
    console.log("User responses:", responses)
    // Optionally send responses to the backend
  }

  return (
    <div className={styles.diagnosticTest}>
      <h2 className={styles.title}>Diagnostic Test</h2>
      {!submitted ? (
        <>
          {questions.map((question, index) => (
            <QuestionCard
              key={index}
              question={question}
              index={index}
              selectedAnswer={responses[index]}
              onAnswerChange={handleAnswerChange}
            />
          ))}
          <SubmitButton onClick={handleSubmit} />
        </>
      ) : (
        <p>Thank you for completing the test!</p>
      )}
    </div>
  )
}
