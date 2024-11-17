import React from "react"
import { useNavigate } from "react-router-dom"

function Home() {
  const navigate = useNavigate()

  return (
    <div className="hero">
      <h2>Welcome to innit</h2>
      <p>Learn practical language skills that are relevant to everyday life!</p>
      <button onClick={() => navigate("/diagnostic")}>Get Started</button>
    </div>
  )
}

export default Home
