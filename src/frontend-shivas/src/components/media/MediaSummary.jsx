import React, { useState } from "react"
import PropTypes from "prop-types"

export default function Summary({ summary }) {
  const [isVisible, setIsVisible] = useState(false)

  if (!summary) return null

  return (
    <section className="w-full max-w-3xl text-left mt-8">
      <button
        onClick={() => setIsVisible(!isVisible)}
        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
      >
        {isVisible ? "Hide Summary" : "View Summary"}
      </button>
      {isVisible && (
        <div className="mt-4 bg-gray-700 p-4 rounded-lg shadow-md">
          <p style={{fontFamily: "Georgia, serif", fontSize: "24px", color:"#f3f4f6"}}>{summary}</p>
        </div>
      )}
    </section>
  )
}

Summary.propTypes = {
  summary: PropTypes.string,
}
