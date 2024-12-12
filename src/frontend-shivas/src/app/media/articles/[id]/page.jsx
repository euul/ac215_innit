"use client"

import React, { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import ArticleText from "@/components/media/ArticleText"
import ArticleSummary from "@/components/media/MediaSummary"
import ArticleKeyWords from "@/components/media/MediaKeyWords"
import ArticleQA from "@/components/media/MediaQA"
import styles from "./styles.module.css"

export default function ArticleDetailPage({ params }) {
  const { id } = params
  const [article, setArticle] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    if (!id) return

    setLoading(true)
    const username = localStorage.getItem("username") // Get username from localStorage

    fetch(`${process.env.NEXT_PUBLIC_BASE_API_URL}/articles/${id}`, {
      headers: {
        "Content-Type": "application/json",
        "X-Username": username, // Include the username in the request headers
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch article")
        }
        return response.json()
      })
      .then((data) => {
        setArticle(data.article)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [id])

  if (loading) {
    return (
      <div className="text-center mt-12">
        <h2 className="text-blue-600 text-xl">Loading article...</h2>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center mt-12">
        <h2 className="text-red-600 text-xl">Something went wrong:</h2>
        <p className="text-gray-600 mt-4">{error}</p>
        <button
          onClick={() => router.push("/media")}
          className="mt-6 px-4 py-2 bg-blue-600 text-white rounded-md"
        >
          Go Back to Media
        </button>
      </div>
    )
  }

  if (!article) {
    return (
      <div className="text-center mt-12">
        <h2 className="text-gray-700 text-xl">Article not found</h2>
        <button
          onClick={() => router.push("/media")}
          className="mt-6 px-4 py-2 bg-blue-600 text-white rounded-md"
        >
          Go Back to Media
        </button>
      </div>
    )
  }

  return (
    <div className={styles.articlePage}>
      {/* Article Title */}
      <header className={styles.articleHeader}>
        <h1 className={styles.articleTitle}>
          {article.Title || "Untitled Article"}
        </h1>
      </header>

      {/* Article Text */}
      <ArticleText text={article.Text} />

      {/* Additional Information in Two Columns */}
      <div className={styles.additionalInfo}>
        {/* Left Column */}
        <div className={styles.leftColumn}>
          <ArticleKeyWords vocab={article.vocab} />
          <ArticleSummary summary={article.summary} />
        </div>

        {/* Right Column */}
        <div className={styles.rightColumn}>
          <ArticleQA questions={article.questions} />
        </div>
      </div>
    </div>
  )
}
