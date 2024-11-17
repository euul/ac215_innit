import React from "react"
import { Link } from "react-router-dom"
import logo from "../images/innit_logo.png"

function Header() {
  return (
    <header>
      <img src={logo} alt="Innit Logo" />
      <nav>
        <Link to="/">Home</Link>
        <Link to="/diagnostic">Diagnostic Test</Link>
        <Link to="/media">Media</Link>
      </nav>
    </header>
  )
}

export default Header
