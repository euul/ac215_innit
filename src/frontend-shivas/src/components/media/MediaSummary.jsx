import React, { useState } from "react"
import PropTypes from "prop-types"

export default function Summary({ summary }) {
  const [isVisible, setIsVisible] = useState(false)

  if (!summary) return null

  return (
    <section className="w-full max-w-3xl text-left mt-8">
      <button
        onClick={() => setIsVisible(!isVisible)}
        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        {isVisible ? "Hide Summary" : "View Summary"}
      </button>
      {isVisible && (
        <div className="mt-4 bg-gray-100 p-4 rounded-lg shadow-md">
          <p className="text-gray-700 leading-relaxed">{summary}</p>
        </div>
      )}
    </section>
  )
}

Summary.propTypes = {
  summary: PropTypes.string,
}
