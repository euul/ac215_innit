import React from "react"
import PropTypes from "prop-types"

export default function KeyWords({ vocab }) {
  if (!vocab) return null

  return (
    <section className="w-full max-w-3xl text-left mt-8">
      <h3 className="text-xl text-gray-800 mb-4">Key Words:</h3>
      <ul className="list-disc pl-8 text-gray-600">
        {vocab.split("\n").map((word, index) => (
          <li key={index} className="mb-2">
            {word}
          </li>
        ))}
      </ul>
    </section>
  )
}

KeyWords.propTypes = {
  vocab: PropTypes.string,
}
