import React, { useState, useEffect } from "react"
import { getToken } from "../utils/auth" // Assuming getToken retrieves the JWT token

function Footer() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userData, setUserData] = useState({ language_level: "NA", xp: 0 }) // Default values

  useEffect(() => {
    // Check if the user is logged in when the component is mounted
    const token = getToken()
    setIsLoggedIn(!!token)

    if (token) {
      // Fetch user data using the token
      fetch("http://localhost:5001/users/me", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`, // Pass the token for authentication
        },
      })
        .then((response) => {
          if (!response.ok) throw new Error("Failed to fetch user data")
          return response.json()
        })
        .then((data) => {
          setUserData({
            language_level: data.language_level || "NA",
            xp: data.xp || 0,
          })
        })
        .catch((error) => {
          console.error("Error fetching user data:", error)
        })
    }
  }, [])

  if (!isLoggedIn) return null // If the user is not logged in, return null (hide footer)

  const { language_level, xp } = userData

  return (
    <footer
      style={{
        position: "fixed", // Keeps it fixed to the screen
        bottom: 0,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        backgroundColor: "#333",
        color: "#fff",
        padding: "2rem 2rem",
        borderTop: "4px solid #00ffcc",
        fontFamily: "Press Start 2P",
        zIndex: 1000, // Ensures it's above other elements
      }}
    >
      {/* User Level */}
      <div style={{ fontSize: "1.2rem" }}>
        Level: <span style={{ color: "#00ffcc" }}>{language_level}</span>
      </div>

      {/* XP Progress */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          width: "25%",
          fontSize: "1.2rem",
        }}
      >
        <span
          style={{
            marginRight: "10px", // Add spacing after "XP:"
            fontSize: "1.2rem",
          }}
        >
          XP:
        </span>
        <div
          style={{
            height: "20px",
            width: "100%",
            backgroundColor: "#555",
            border: "2px solid #000",
            borderRadius: "10px",
            overflow: "hidden",
            position: "relative",
          }}
        >
          <div
            style={{
              height: "100%",
              width: `${Math.min(xp, 100)}%`, // Ensure XP doesn't exceed 100% visually
              backgroundColor: "#00ffcc",
              transition: "width 0.5s ease",
              clipPath: "polygon(0% 0%, 100% 0%, 95% 100%, 0% 100%)", // Slanted edge
            }}
          ></div>
        </div>
        <span
          style={{
            marginLeft: "10px",
            fontSize: "1.2rem",
            color: "#00ffcc",
          }}
        >
          {xp}
        </span>
        <span
          style={{
            marginLeft: "10px",
            fontSize: "1.2rem",
            color: "#ffcc00",
          }}
        >
          /100
        </span>
      </div>
    </footer>
  )
}

export default Footer
