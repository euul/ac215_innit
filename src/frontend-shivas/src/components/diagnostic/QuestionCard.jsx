import React from "react"
import PropTypes from "prop-types"
import styles from "./QuestionCard.module.css"

export default function QuestionCard({
  questionData,
  index,
  selectedAnswer,
  result,
  onAnswerChange,
}) {
  if (!questionData) {
    return <div className={styles.error}>Question data is missing!</div>
  }

  const { question, choices } = questionData

  const handleAnswerSelect = (value) => {
    if (!selectedAnswer) {
      onAnswerChange(index, value)
    }
  }

  return (
    <div className={styles.questionCard}>
      <h4 className={styles.questionText}>{`${index + 1}. ${question}`}</h4>
      <ul className={styles.choicesList}>
        {choices.map((choice, choiceIndex) => (
          <li key={choiceIndex} className={styles.choiceItem}>
            <label className={styles.choiceLabel}>
              <input
                type="radio"
                name={`question-${index}`}
                value={String.fromCharCode(65 + choiceIndex)} // Convert index to A, B, C, etc.
                checked={
                  selectedAnswer === String.fromCharCode(65 + choiceIndex)
                }
                onChange={(e) => handleAnswerSelect(e.target.value)}
                disabled={!!selectedAnswer} // Disable input after selection
              />
              <span>{choice}</span>
            </label>
          </li>
        ))}
      </ul>
      {result && (
        <p
          className={`${styles.resultText} ${
            result.includes("Correct!") ? styles.correct : styles.incorrect
          }`}
        >
          {result}
        </p>
      )}
    </div>
  )
}

QuestionCard.propTypes = {
  questionData: PropTypes.shape({
    question: PropTypes.string.isRequired,
    choices: PropTypes.arrayOf(PropTypes.string).isRequired,
    answer: PropTypes.string.isRequired,
  }).isRequired,
  index: PropTypes.number.isRequired,
  selectedAnswer: PropTypes.string,
  result: PropTypes.string,
  onAnswerChange: PropTypes.func.isRequired,
}
