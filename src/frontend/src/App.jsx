import React from "react"
import "./styles/styles.css"
import { BrowserRouter as Router, Route, Routes } from "react-router-dom"
import Header from "./components/Header"
import Home from "./pages/Home"
import DiagnosticTest from "./pages/DiagnosticTest"
import Media from "./pages/Media"

function App() {
  return (
    <Router>
      <div
        style={{ display: "flex", flexDirection: "column", height: "100vh" }}
      >
        <Header />
        <div style={{ padding: "1rem", flex: 1 }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/diagnostic" element={<DiagnosticTest />} />
            <Route path="/media" element={<Media />} />
          </Routes>
        </div>
      </div>
    </Router>
  )
}

export default App
