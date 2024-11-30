import React from "react"
import { BrowserRouter as Router, Route, Routes } from "react-router-dom"
import Header from "./components/Header"
import Footer from "./components/Footer"
import Home from "./pages/Home"
import DiagnosticTest from "./pages/DiagnosticTest"
import Media from "./pages/Media"
import MediaDetail from "./pages/MediaDetail"
import Login from "./pages/LogIn"
import Register from "./pages/Register"

function App() {
  return (
    <Router>
      <div
        style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}
      >
        <Header />
        <div style={{ flex: 1 }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/diagnostic" element={<DiagnosticTest />} />
            <Route path="/media" element={<Media />} />
            <Route path="/media/:id" element={<MediaDetail />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Routes>
        </div>
        <Footer />
      </div>
    </Router>
  )
}

export default App
