import React, { useState } from "react"
import PropTypes from "prop-types"

export default function QASection({ questions }) {
  const parsedQuestions = JSON.parse(questions || "[]")

  return (
    <section className="w-full max-w-3xl text-left mt-8">
      <h3 className="text-xl text-gray-800 mb-4">Test Your Knowledge:</h3>
      {parsedQuestions.map((q, index) => (
        <QuestionCard key={index} questionData={q} />
      ))}
    </section>
  )
}

function QuestionCard({ questionData }) {
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
  }

  return (
    <div className="mb-6 p-4 bg-gray-100 rounded-lg shadow-md">
      <h4 className="text-lg text-gray-800">{question}</h4>
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
      {result && <p className="mt-2 text-gray-700">{result}</p>}
    </div>
  )
}

QASection.propTypes = {
  questions: PropTypes.string,
}

QuestionCard.propTypes = {
  questionData: PropTypes.shape({
    question: PropTypes.string.isRequired,
    choices: PropTypes.arrayOf(PropTypes.string).isRequired,
    answer: PropTypes.string.isRequired,
  }),
}
