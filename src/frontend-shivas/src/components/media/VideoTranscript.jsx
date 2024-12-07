import React, { useEffect, useRef } from "react"
import PropTypes from "prop-types"
import styles from "./VideoTranscript.module.css" // Import CSS module

export default function VideoTranscript({ transcript, currentIndex }) {
  const transcriptRef = useRef(null)

  useEffect(() => {
    if (currentIndex !== -1 && transcriptRef.current) {
      const entryElement = transcriptRef.current.querySelectorAll(
        `.${styles.transcriptEntry}`
      )[currentIndex]
      entryElement?.scrollIntoView({ behavior: "smooth", block: "center" })
    }
  }, [currentIndex])

  return (
    <div ref={transcriptRef} className={styles.transcriptContainer}>
      {transcript.map((entry, index) => (
        <div
          key={index}
          className={`${styles.transcriptEntry} ${
            index === currentIndex ? styles.active : ""
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
