"use client"

import { usePathname } from "next/navigation"
import React, { useState, useEffect } from "react"
import styles from "./Footer.module.css"

export default function Footer() {
  const pathname = usePathname()
  const hideFooter = pathname === "/chat"
  const [userData, setUserData] = useState({ language_level: "NA", xp: 0 })

  const levelMappings = {
    B1: { label: "Easy", style: styles.easy },
    B2: { label: "Intermediate", style: styles.intermediate },
    C1: { label: "Advanced", style: styles.advanced },
    NA: { label: "NA", style: styles.na },
  }

  const fetchUserData = async () => {
    const username = localStorage.getItem("username")
    if (!username) {
      setUserData({ language_level: "NA", xp: 0 })
      return
    }

    try {
      const response = await fetch(
        `${
          process.env.NEXT_PUBLIC_BASE_API_URL
        }/get-metadata?username=${encodeURIComponent(username)}`
      )
      if (response.ok) {
        const data = await response.json()
        setUserData({
          language_level: data.metadata?.level || "NA",
          xp: data.metadata?.xp || 0,
        })
      } else {
        console.error("Failed to fetch user data:", response.statusText)
        setUserData({ language_level: "NA", xp: 0 })
      }
    } catch (error) {
      console.error("Error fetching user data:", error)
      setUserData({ language_level: "NA", xp: 0 })
    }
  }

  useEffect(() => {
    fetchUserData() // Fetch metadata on component mount
  }, [pathname]) // Refetch metadata when the route changes

  if (hideFooter) {
    return null
  }

  const { language_level, xp } = userData
  const { label, style } = levelMappings[language_level] || levelMappings["NA"]

  return (
    <footer className={styles.footer}>
      <div className={styles.level}>
        Level: <span className={`${styles.levelValue} ${style}`}>{label}</span>
      </div>
      <div className={styles.xpBarContainer}>
        <span className={styles.xpLabel}>XP:</span>
        <div className={styles.xpBar}>
          <div
            className={styles.xpProgress}
            style={{ width: `${Math.min(xp, 100)}%` }}
          ></div>
        </div>
        <span className={styles.xpValue}>{xp}</span>
        <span className={styles.xpMax}>/100</span>
      </div>
    </footer>
  )
}
