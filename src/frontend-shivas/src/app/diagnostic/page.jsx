"use client"

import React, { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import QuestionCard from "@/components/diagnostic/QuestionCard"
import styles from "./styles.module.css"
import DataService from "@/services/DataService"

export default function DiagnosticTestPage() {
  const [questions, setQuestions] = useState([])
  const [responses, setResponses] = useState({})
  const [results, setResults] = useState({})
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [userLevel, setUserLevel] = useState("")
  const router = useRouter()

  // Utility to shuffle choices and track the correct answer
  const shuffleChoices = (choices, correctAnswer) => {
    const choiceObjects = choices.map((choice, index) => ({
      choice,
      isCorrect: String.fromCharCode(65 + index) === correctAnswer,
    }))

    for (let i = choiceObjects.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      ;[choiceObjects[i], choiceObjects[j]] = [
        choiceObjects[j],
        choiceObjects[i],
      ]
    }

    const shuffledChoices = choiceObjects.map((item) => item.choice)
    const correctIndex = choiceObjects.findIndex((item) => item.isCorrect)
    const newCorrectAnswer = String.fromCharCode(65 + correctIndex)

    return { shuffledChoices, newCorrectAnswer }
  }

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const response = await DataService.GetDiagnosticTestQuestions()
        const rawQuestions = response.data.questions || []

        const processedQuestions = rawQuestions.map((q) => {
          const { shuffledChoices, newCorrectAnswer } = shuffleChoices(
            q.choices,
            q.answer
          )
          return { ...q, choices: shuffledChoices, answer: newCorrectAnswer }
        })

        setQuestions(processedQuestions)
      } catch (error) {
        console.error("Error fetching questions:", error)
      }
    }

    fetchQuestions()
  }, [])

  const handleAnswerChange = (index, selectedAnswer) => {
    const correctAnswer = questions[index]?.answer

    setResponses((prev) => ({
      ...prev,
      [index]: selectedAnswer,
    }))

    setResults((prev) => ({
      ...prev,
      [index]:
        selectedAnswer === correctAnswer
          ? "Correct!"
          : `Wrong! The correct answer is ${correctAnswer}.`,
    }))
  }

  const submitAllResponses = async () => {
    if (Object.keys(responses).length < questions.length) {
      alert("Please answer all questions before submitting!")
      return
    }

    let correctCount = 0
    Object.keys(responses).forEach((index) => {
      if (responses[index] === questions[index]?.answer) {
        correctCount++
      }
    })

    // Determine user level based on correctCount
    let userLevel = "B1"
    let levelDescription = "easy"
    if (correctCount > 8) {
      userLevel = "C1"
      levelDescription = "advanced"
    } else if (correctCount > 5) {
      userLevel = "B2"
      levelDescription = "intermediate"
    }

    setUserLevel(
      <>
        Your level is:{" "}
        <span className={styles.levelHighlight}>{levelDescription}</span>
      </>
    )

    setIsSubmitted(true)

    try {
      const username = localStorage.getItem("username")
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BASE_API_URL}/update-metadata`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username,
            metadata: { level: userLevel, xp: 0 },
          }),
        }
      )

      if (response.ok) {
        console.log("User level updated successfully!")
      } else {
        const data = await response.json()
        console.error("Error updating user level:", data.detail)
      }
    } catch (error) {
      console.error("Error during metadata update:", error)
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
          />
        ))}
      </div>
      {!isSubmitted && (
        <button className={styles.submitAllButton} onClick={submitAllResponses}>
          Submit All
        </button>
      )}
      {isSubmitted && (
        <div className={styles.resultsContainer}>
          <p className={styles.thankYou}>Thank you for completing the test!</p>
          <p className={styles.userLevel}>{userLevel}</p>
          <button
            className={styles.homeButton}
            onClick={() => router.push("/")}
          >
            Home Page
          </button>
        </div>
      )}
    </div>
  )
}
