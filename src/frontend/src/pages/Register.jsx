import React, { useState } from "react"
import { useNavigate } from "react-router-dom"

function Register() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const navigate = useNavigate()

  const handleRegister = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch("http://localhost:5001/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      })
      const data = await response.json()
      if (response.ok) {
        setSuccess("Account created successfully! Redirecting to login...")
        setTimeout(() => navigate("/login"), 2000) // Redirect to login page
      } else {
        setError(data.message || "Registration failed")
      }
    } catch (err) {
      setError("An error occurred. Please try again.")
    }
  }

  return (
    <div style={{ textAlign: "center", marginTop: "2rem" }}>
      <h2>Register</h2>
      <form
        onSubmit={handleRegister}
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
          Register
        </button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {success && <p style={{ color: "green" }}>{success}</p>}
      <p style={{ marginTop: "1rem" }}>
        Already have an account? <a href="/login">Log in here</a>
      </p>
    </div>
  )
}

export default Register
