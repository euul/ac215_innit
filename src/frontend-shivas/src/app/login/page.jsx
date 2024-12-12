"use client"

import React, { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import styles from "./styles.module.css"

export default function LoginPage() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const router = useRouter()

  const handleLogin = async (e) => {
    e.preventDefault()
    setError("")

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BASE_API_URL}/login`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password }),
        }
      )

      const data = await response.json()

      if (response.ok) {
        // Save the token and username to localStorage
        localStorage.setItem("token", data.token)
        localStorage.setItem("username", username)

        // Redirect to the homepage
        router.push("/")
      } else {
        setError(data.detail || "Login failed. Please try again.")
      }
    } catch (err) {
      console.error("Error during login:", err)
      setError("An unexpected error occurred. Please try again later.")
    }
  }

  return (
    <div className={styles.loginPage}>
      <form onSubmit={handleLogin} className={styles.formContainer}>
        <h2>Login</h2>
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
        <button type="submit">Login</button>
        <p className={styles.registerMessage}>
          Don't have an account?{" "}
          <Link href="/register" className={styles.registerLink}>
            Register here
          </Link>
        </p>
      </form>
    </div>
  )
}
