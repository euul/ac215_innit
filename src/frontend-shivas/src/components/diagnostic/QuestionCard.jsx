import React from "react"
import { Typography, RadioGroup, FormControlLabel, Radio } from "@mui/material"

export default function QuestionCard({
  question,
  index,
  selectedAnswer,
  onAnswerChange,
}) {
  return (
    <div>
      <Typography variant="h6">{`${index + 1}. ${
        question.question
      }`}</Typography>
      <RadioGroup
        value={selectedAnswer || ""}
        onChange={(e) => onAnswerChange(index, e.target.value)}
      >
        {question.choices.map((choice, choiceIndex) => (
          <FormControlLabel
            key={choiceIndex}
            value={String.fromCharCode(65 + choiceIndex)} // Convert index to A, B, C, etc.
            control={<Radio />}
            label={choice}
          />
        ))}
      </RadioGroup>
    </div>
  )
}
