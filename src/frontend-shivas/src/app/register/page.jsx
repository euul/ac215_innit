"use client"

import React, { useState } from "react"
import { useRouter } from "next/navigation" // For navigation
import Link from "next/link"
import styles from "./styles.module.css"

export default function RegisterPage() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const router = useRouter() // Use router for navigation

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BASE_API_URL}/register`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password }), // Only send username and password
        }
      )

      const data = await response.json()

      if (response.ok) {
        // Redirect to login page upon successful registration
        router.push("/login")
      } else {
        setError(data.detail || "Registration failed. Please try again.")
      }
    } catch (err) {
      console.error("Error during registration:", err)
      setError("An unexpected error occurred. Please try again later.")
    }
  }

  return (
    <div className={styles.registerPage}>
      <form onSubmit={handleSubmit} className={styles.formContainer}>
        <h2>Register</h2>
        {error && <p className={styles.error}>{error}</p>}
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
        />
        <button type="submit">Register</button>
        <p className={styles.loginMessage}>
          Already have an account?{" "}
          <Link href="/login" className={styles.loginLink}>
            Log in here
          </Link>
        </p>
      </form>
    </div>
  )
}
