import React, { useState } from "react"
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom"
import Header from "./components/Header"
import Footer from "./components/Footer"
import Home from "./pages/Home"
import DiagnosticTest from "./pages/DiagnosticTest"
import Media from "./pages/Media"
import MediaDetail from "./pages/MediaDetail"
import Login from "./pages/LogIn"
import Register from "./pages/Register"

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem("token"))

  const handleLogin = () => {
    setIsLoggedIn(true) // Update state when the user logs in
  }

  const handleLogout = () => {
    setIsLoggedIn(false) // Update state when the user logs out
    localStorage.removeItem("token") // Clear the token on logout
  }

  return (
    <Router>
      <div
        style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}
      >
        <Header isLoggedIn={isLoggedIn} handleLogout={handleLogout} />
        <div style={{ flex: 1 }}>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Home />} />
            <Route
              path="/login"
              element={<Login handleLogin={handleLogin} />}
            />
            <Route path="/register" element={<Register />} />

            {/* Protected routes */}
            <Route
              path="/diagnostic"
              element={
                isLoggedIn ? <DiagnosticTest /> : <Navigate to="/login" />
              }
            />
            <Route
              path="/media"
              element={isLoggedIn ? <Media /> : <Navigate to="/login" />}
            />
            <Route
              path="/media/:id"
              element={isLoggedIn ? <MediaDetail /> : <Navigate to="/login" />}
            />
          </Routes>
        </div>
        {isLoggedIn && <Footer />}
      </div>
    </Router>
  )
}

export default App
