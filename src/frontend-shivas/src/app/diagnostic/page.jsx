"use client"

import React, { useEffect, useState } from "react"
import QuestionCard from "@/components/diagnostic/QuestionCard"
import styles from "./styles.module.css"
import DataService from "@/services/DataService"

export default function DiagnosticTestPage() {
  const [questions, setQuestions] = useState([])
  const [responses, setResponses] = useState({})
  const [results, setResults] = useState({})

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

  const handleSubmit = (index) => {
    const selectedAnswer = responses[index]
    if (!selectedAnswer) {
      setResults((prev) => ({
        ...prev,
        [index]: "Please select an answer!",
      }))
      return
    }

    const correctAnswer = questions[index]?.answer
    if (selectedAnswer === correctAnswer) {
      setResults((prev) => ({
        ...prev,
        [index]: "Correct!",
      }))
    } else {
      setResults((prev) => ({
        ...prev,
        [index]: `Wrong! The correct answer is ${correctAnswer}.`,
      }))
    }
  }

  return (
    <div className={styles.diagnosticTest}>
      <h2 className={styles.title}>Diagnostic Test</h2>
      <div className={styles.questionGrid}>
        {questions.map((question, index) => (
          <QuestionCard
            key={index}
            questionData={question}
            index={index}
            selectedAnswer={responses[index]}
            result={results[index]}
            onAnswerChange={handleAnswerChange}
            onSubmit={handleSubmit}
          />
        ))}
      </div>
    </div>
  )
}
