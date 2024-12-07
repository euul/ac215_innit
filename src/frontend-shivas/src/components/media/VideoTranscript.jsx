import React, { useEffect, useRef } from "react"
import PropTypes from "prop-types"

export default function VideoTranscript({ transcript, currentIndex }) {
  const transcriptRef = useRef(null)

  useEffect(() => {
    if (currentIndex !== -1 && transcriptRef.current) {
      const entryElement =
        transcriptRef.current.querySelectorAll(".transcript-entry")[
          currentIndex
        ]
      entryElement?.scrollIntoView({ behavior: "smooth", block: "center" })
    }
  }, [currentIndex])

  return (
    <div ref={transcriptRef} className="transcript-container">
      {transcript.map((entry, index) => (
        <div
          key={index}
          className={`transcript-entry ${
            index === currentIndex ? "active" : ""
          }`}
        >
          <p>{entry.text}</p>
        </div>
      ))}
    </div>
  )
}

VideoTranscript.propTypes = {
  transcript: PropTypes.arrayOf(
    PropTypes.shape({
      text: PropTypes.string.isRequired,
      start: PropTypes.string.isRequired,
    })
  ).isRequired,
  currentIndex: PropTypes.number.isRequired,
}
