"use client"

import React, { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import ArticleDetailContent from "@/components/media/ArticleDetailContent"
import styles from "./styles.module.css"

export default function ArticleDetailPage({ params }) {
  const { id } = params // Get the article ID from the URL
  const [article, setArticle] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    if (!id) return

    setLoading(true)
    fetch(`${process.env.NEXT_PUBLIC_BASE_API_URL}/articles/${id}`)
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
      <ArticleDetailContent article={article} />
    </div>
  )
}
