import { Link } from "react-router-dom"
import "../styles/styles.css"
import logo from "../images/innit_logo.png"

const Header = ({ isLoggedIn, handleLogout }) => {
  return (
    <header>
      <img src={logo} alt="Logo" />
      <nav>
        <Link to="/">Home</Link>
        {isLoggedIn && <Link to="/diagnostic">Diagnostic</Link>}
        {isLoggedIn && <Link to="/media">Media</Link>}
        {isLoggedIn ? (
          // Use a Link for the logout functionality, styled like other links
          <Link to="/" onClick={handleLogout}>
            Log out
          </Link>
        ) : (
          <Link to="/login">Log in</Link>
        )}
      </nav>
    </header>
  )
}

export default Header
