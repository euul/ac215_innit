import React, { useState, useEffect } from "react"
import PropTypes from "prop-types"

export default function MediaQA({ questions }) {
  const parsedQuestions = JSON.parse(questions || "[]")
  const [currentXP, setCurrentXP] = useState(0)
  const username = localStorage.getItem("username") // Get the username from localStorage

  // Fetch the user's current XP when the component mounts
  useEffect(() => {
    const fetchCurrentXP = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_BASE_API_URL}/get-metadata?username=${username}`
        )
        if (response.ok) {
          const data = await response.json()
          setCurrentXP(data.metadata?.xp || 0)
        } else {
          console.error("Failed to fetch current XP:", response.statusText)
        }
      } catch (error) {
        console.error("Error fetching current XP:", error)
      }
    }

    fetchCurrentXP()
  }, [username])

  const handleAnswerSubmit = async (
    question,
    selectedAnswer,
    correctAnswer
  ) => {
    if (selectedAnswer === correctAnswer) {
      // Increment XP by 2
      const newXP = currentXP + 2

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_BASE_API_URL}/update-metadata`,
          {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              username,
              metadata: { xp: newXP }, // Update XP in metadata
            }),
          }
        )

        if (response.ok) {
          console.log("XP updated successfully!")
          setCurrentXP(newXP) // Update state to reflect new XP
        } else {
          const data = await response.json()
          console.error("Error updating XP:", data.detail)
        }
      } catch (error) {
        console.error("Error during XP update:", error)
      }
    }
  }

  return (
    <section className="w-full max-w-3xl text-left mt-8">
      <h3 className="text-xl text-green-500 mb-4">Test Your Knowledge:</h3>
      {parsedQuestions.map((q, index) => (
        <QuestionCard
          key={index}
          questionData={q}
          onAnswerSubmit={handleAnswerSubmit}
        />
      ))}
    </section>
  )
}

function QuestionCard({ questionData, onAnswerSubmit }) {
  const { question, choices, answer } = questionData
  const [selected, setSelected] = useState(null)
  const [result, setResult] = useState("")

  const handleSubmit = () => {
    if (!selected) {
      setResult("Please select an answer!")
      return
    }

    if (selected === answer) {
      setResult("Correct!")
    } else {
      setResult(`Wrong! The correct answer is ${answer}.`)
    }

    onAnswerSubmit(question, selected, answer) // Trigger XP update if correct
  }

  return (
    <div className="mb-6 p-4 bg-gray-700 rounded-lg shadow-md">
      <h4 className="text-lg text-gray-100">{question}</h4>
      <ul className="list-none mt-2">
        {choices.map((choice, idx) => (
          <li key={idx}>
            <label className="flex items-center space-x-2">
              <input
                type="radio"
                name={`question-${question}`}
                value={choice.charAt(0)} // Extract "A", "B", "C"
                onChange={() => setSelected(choice.charAt(0))}
              />
              <span>{choice}</span>
            </label>
          </li>
        ))}
      </ul>
      <button
        onClick={handleSubmit}
        className="mt-4 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
      >
        Submit
      </button>
      {result && <p className="mt-2 retroYellow">{result}</p>}
    </div>
  )
}

MediaQA.propTypes = {
  questions: PropTypes.string,
}

QuestionCard.propTypes = {
  questionData: PropTypes.shape({
    question: PropTypes.string.isRequired,
    choices: PropTypes.arrayOf(PropTypes.string).isRequired,
    answer: PropTypes.string.isRequired,
  }),
  onAnswerSubmit: PropTypes.func.isRequired,
}
