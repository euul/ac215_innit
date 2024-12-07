"use client"

import React, { useState, useEffect } from "react"
import VideoPlayer from "@/components/media/VideoPlayer"
import VideoTranscript from "@/components/media/VideoTranscript"
import styles from "./styles.module.css"

export default function VideoDetailPage({ params }) {
  const { id } = params
  const [video, setVideo] = useState(null)
  const [currentTime, setCurrentTime] = useState(0)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_BASE_API_URL}/videos/${id}`)
      .then((response) => {
        if (!response.ok) throw new Error("Failed to fetch video")
        return response.json()
      })
      .then((data) => setVideo(data.video))
      .catch((err) => setError(err.message))
  }, [id])

  if (error) {
    return <div>Error: {error}</div>
  }

  if (!video) {
    return <div>Loading...</div>
  }

  const processedTranscript = video.transcript.map((entry) => ({
    ...entry,
    startInSeconds: parseFloat(entry.start),
  }))

  const currentIndex = processedTranscript.findIndex(
    (entry, i) =>
      currentTime >= entry.startInSeconds &&
      (i === processedTranscript.length - 1 ||
        currentTime < processedTranscript[i + 1].startInSeconds)
  )

  return (
    <div className={styles.videoPage}>
      <h2 className={styles.videoTitle}>{video.video_name}</h2>
      <div className={styles.videoContent}>
        <VideoPlayer
          videoId={video.video_id}
          onTimeUpdate={(time) => setCurrentTime(time)}
        />
        <VideoTranscript
          transcript={processedTranscript}
          currentIndex={currentIndex}
        />
      </div>
    </div>
  )
}
