"use client"

import React, { useEffect, useState } from "react"
import MediaList from "@/components/media/MediaList"
import styles from "./styles.module.css"

export default function MediaPage() {
  const [articles, setArticles] = useState([])
  const [videos, setVideos] = useState([])
  const [username, setUsername] = useState(null)

  // Utility function to shuffle and pick a subset
  const getRandomSubset = (data, count) => {
    const shuffled = data.sort(() => 0.5 - Math.random()) // Shuffle array
    return shuffled.slice(0, count) // Return the first 'count' items
  }

  useEffect(() => {
    // Get the username from localStorage
    const storedUsername = localStorage.getItem("username")
    setUsername(storedUsername)

    if (!storedUsername) {
      console.error("Username not found in localStorage")
      return
    }

    // Fetch articles
    fetch(
      `${process.env.NEXT_PUBLIC_BASE_API_URL}/articles?username=${storedUsername}`
    )
      .then((response) => response.json())
      .then((data) => setArticles(data.articles.slice(0, 5)))
      .catch((error) => console.error("Error fetching articles:", error))

    // Fetch videos
    fetch(
      `${process.env.NEXT_PUBLIC_BASE_API_URL}/transcripts?username=${storedUsername}`
    )
      .then((response) => response.json())
      .then((data) => setVideos(data.transcripts.slice(0, 5)))
      .catch((error) =>
        console.error("Error fetching video transcripts:", error)
      )
  }, [])

  return (
    <div className={styles.mediaPage}>
      <div className="container mx-auto px-4 py-8">
        <h2 className="text-3xl font-bold text-green-500 text-center mb-6">
          Media
        </h2>
        <p className="text-lg text-yellow-500 text-center mb-8">
          Browse and select a video or article to explore.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Articles */}
          <MediaList title="Articles" items={articles} type="article" />
          {/* Videos */}
          <MediaList title="Videos" items={videos} type="video" />
        </div>
      </div>
    </div>
  )
}
