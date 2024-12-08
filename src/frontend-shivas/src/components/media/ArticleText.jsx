import React from "react"
import PropTypes from "prop-types"

export default function ArticleText({ text }) {
  if (!text) {
    return <p className="text-gray-500 text-lg mt-4">No content available.</p>
  }

  return (
    <section className="max-h-96 overflow-y-auto w-full max-w-3xl p-6 bg-gray-100 rounded-lg shadow-md mb-8">
      {text.split("\n").map((paragraph, index) => (
        <p
          key={index}
          className="mb-6 text-gray-700 text-lg leading-relaxed text-justify"
        >
          {paragraph}
        </p>
      ))}
    </section>
  )
}

ArticleText.propTypes = {
  text: PropTypes.string.isRequired,
}
