"use client"

import React, { useState, useEffect } from "react"
import VideoPlayer from "@/components/media/VideoPlayer"
import VideoTranscript from "@/components/media/VideoTranscript"
import KeyWords from "@/components/media/MediaKeyWords"
import Summary from "@/components/media/MediaSummary"
import QASection from "@/components/media/MediaQA"
import styles from "./styles.module.css"

export default function VideoDetailPage({ params }) {
  const { id } = params
  const [video, setVideo] = useState(null)
  const [currentTime, setCurrentTime] = useState(0)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_BASE_API_URL}/videos/${id}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch video")
        }
        return response.json()
      })
      .then((data) => setVideo(data.video))
      .catch((err) => setError(err.message))
  }, [id])

  if (error) {
    return <div className={styles.error}>Error: {error}</div>
  }

  if (!video) {
    return <div className={styles.loading}>Loading...</div>
  }

  // Convert "hh:mm:ss" to seconds
  const convertToSeconds = (timeString) => {
    const parts = timeString.split(":").map(Number)
    if (parts.length === 3) {
      const [hours, minutes, seconds] = parts
      return hours * 3600 + minutes * 60 + seconds
    } else if (parts.length === 2) {
      const [minutes, seconds] = parts
      return minutes * 60 + seconds
    }
    return parseFloat(timeString)
  }

  // Process the transcript to include start time in seconds
  const processedTranscript = video.transcript.map((entry) => ({
    ...entry,
    startInSeconds: convertToSeconds(entry.start),
  }))

  // Determine the current index of the transcript based on the video time
  const currentIndex = processedTranscript.findIndex(
    (entry, i) =>
      currentTime >= entry.startInSeconds &&
      (i === processedTranscript.length - 1 ||
        currentTime < processedTranscript[i + 1].startInSeconds)
  )

  return (
    <div className={styles.videoPage}>
      {/* Video Title */}
      <h1 className={styles.videoTitle}>{video.video_name}</h1>

      <div className={styles.contentContainer}>
        {/* Video Section */}
        <div className={styles.videoSection}>
          <h2 className={styles.subheading}>Video</h2>
          <div className={styles.videoContainer}>
            <VideoPlayer
              videoId={video.video_id}
              onTimeUpdate={(time) => setCurrentTime(time)}
            />
          </div>
        </div>

        {/* Transcript Section */}
        <div className={styles.transcriptSection}>
          <h2 className={styles.subheading}>Transcript</h2>
          <div className={styles.transcriptContainer}>
            <VideoTranscript
              transcript={processedTranscript}
              currentIndex={currentIndex}
            />
          </div>
        </div>
      </div>

      {/* Additional Information */}
      <div className={styles.additionalInfo}>
        <KeyWords vocab={video.vocab} />
        <Summary summary={video.summary} />
        <QASection questions={video.questions} />
      </div>
    </div>
  )
}
