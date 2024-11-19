import React from "react"
import { useNavigate } from "react-router-dom"

function Home() {
  const navigate = useNavigate()

  return (
    <div className="hero">
      <h2>innit</h2>
      <p>Practical Language Learning</p>
      <button onClick={() => navigate("/diagnostic")}>Get Started</button>
    </div>
  )
}

export default Home
