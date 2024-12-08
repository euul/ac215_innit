// app/login/page.jsx (for App Router or pages/login.js for Pages Router)
"use client"

import React, { useState } from "react"
import { login } from "../auth.js" // Import the login function
import { useRouter } from "next/navigation" // For redirection
import Link from "next/link"
import styles from "./styles.module.css"

export default function LoginPage() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const router = useRouter()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")

    const result = await login(username, password)

    if (result.success) {
      router.push("/") // Redirect to homepage upon successful login
    } else {
      setError(result.error)
    }
  }

  return (
    <div className={styles.loginPage}>
      <form onSubmit={handleSubmit} className={styles.formContainer}>
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
