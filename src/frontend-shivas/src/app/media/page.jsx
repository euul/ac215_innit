"use client"

import React, { useEffect, useState } from "react"
import MediaList from "@/components/media/MediaList"
import styles from "./styles.module.css"

export default function MediaPage() {
  const [articles, setArticles] = useState([])
  const [videos, setVideos] = useState([])

  useEffect(() => {
    // Fetch articles
    fetch(`${process.env.NEXT_PUBLIC_BASE_API_URL}/articles`)
      .then((response) => response.json())
      .then((data) => setArticles(data.articles.slice(0, 5)))
      .catch((error) => console.error("Error fetching articles:", error))

    // Fetch videos
    fetch(`${process.env.NEXT_PUBLIC_BASE_API_URL}/transcripts`)
      .then((response) => response.json())
      .then((data) => setVideos(data.transcripts.slice(0, 5)))
      .catch((error) =>
        console.error("Error fetching video transcripts:", error)
      )
  }, [])

  return (
    <div className={styles.mediaPage}>
      <div className="container mx-auto px-4 py-8">
        <h2 className="text-3xl font-bold text-gray-800 text-center mb-6">
          Media
        </h2>
        <p className="text-lg text-gray-600 text-center mb-8">
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
