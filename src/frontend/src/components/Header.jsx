import React from "react"
import { Link } from "react-router-dom"
import "../styles/styles.css"
import logo from "../images/innit_logo.png"

function Header() {
  return (
    <header>
      <img src={logo} alt="Logo" />
      <nav>
        <Link to="/">Home</Link>
        <Link to="/diagnostic">Diagnostic Test</Link>
        <Link to="/media">Media</Link>
      </nav>
    </header>
  )
}

export default Header
