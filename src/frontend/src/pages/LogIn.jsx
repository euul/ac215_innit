import React, { useState } from "react"
import { useNavigate } from "react-router-dom"

function Login() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch("http://localhost:5001/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      })
      const data = await response.json()
      if (response.ok) {
        localStorage.setItem("token", data.access_token) // Store JWT token
        navigate("/") // Redirect to homepage or dashboard
      } else {
        setError(data.message || "Login failed")
      }
    } catch (err) {
      setError("An error occurred. Please try again.")
    }
  }

  return (
    <div style={{ textAlign: "center", marginTop: "2rem" }}>
      <h2>Log In</h2>
      <form
        onSubmit={handleLogin}
        style={{ display: "inline-block", marginTop: "1rem" }}
      >
        <div>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={{ padding: "0.5rem", marginBottom: "1rem" }}
          />
        </div>
        <div>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ padding: "0.5rem", marginBottom: "1rem" }}
          />
        </div>
        <button type="submit" style={{ padding: "0.5rem 1rem" }}>
          Log In
        </button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <p style={{ marginTop: "1rem" }}>
        Don't have an account? <a href="/register">Register here</a>
      </p>
    </div>
  )
}

export default Login
