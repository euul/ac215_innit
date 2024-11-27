import React from "react"
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import Header from "./components/Header"
import Home from "./pages/Home"
import DiagnosticTest from "./pages/DiagnosticTest"
import Media from "./pages/Media"
import MediaDetail from "./pages/MediaDetail"
import Footer from "./components/Footer"

function App() {
  return (
    <Router>
      <div style={{ paddingBottom: "100px" }}>
        <Header />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/diagnostic" element={<DiagnosticTest />} />
          <Route path="/media" element={<Media />} />
          <Route path="/media/:id" element={<MediaDetail />} />
        </Routes>
        <Footer />
      </div>
    </Router>
  )
}

export default App
