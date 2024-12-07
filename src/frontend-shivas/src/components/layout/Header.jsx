"use client"

import Link from "next/link"
import Image from "next/image"
import { useState, useEffect } from "react"
import { Home, Info, Assignment, VideoLibrary } from "@mui/icons-material"
import styles from "./Header.module.css"

const navItems = [
  { name: "Home", path: "/", icon: <Home fontSize="small" /> },
  {
    name: "About",
    path: "/about",
    icon: <Info fontSize="small" />,
  },
  {
    name: "Diagnostic",
    path: "/diagnostic",
    icon: <Assignment fontSize="small" />,
  },
  {
    name: "Media",
    path: "/media",
    icon: <VideoLibrary fontSize="small" />,
  },
]

export default function Header() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  useEffect(() => {
    if (window) {
      const handleScroll = () => {
        setIsScrolled(window.scrollY > 50)
      }

      window.addEventListener("scroll", handleScroll)
      return () => window.removeEventListener("scroll", handleScroll)
    }
  }, [])

  return (
    <header
      className={`fixed w-full top-0 z-50 transition-all duration-300 ${
        isScrolled ? "bg-retroYellow shadow-md" : "bg-retroYellow"
      }`}
    >
      <div className="container mx-auto px-4 h-20 flex items-center justify-between">
        {/* Logo */}
        <Link href="/">
          <div className="flex items-center space-x-3">
            <Image
              src="/assets/logo.png"
              alt="Innit Logo"
              width={100}
              height={100}
            />
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-8">
          {navItems.map((item) => (
            <Link
              key={item.name}
              href={item.path}
              className="flex items-center text-retroText hover:text-retroGreen transition"
            >
              <span className="mr-2">{item.icon}</span>
              {item.name}
            </Link>
          ))}
        </nav>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden p-2"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-label="Toggle mobile menu"
        >
          <div
            className={`w-6 h-0.5 bg-black mb-1.5 transition-all ${
              isMobileMenuOpen ? "rotate-45 translate-y-2" : ""
            }`}
          />
          <div
            className={`w-6 h-0.5 bg-black mb-1.5 ${
              isMobileMenuOpen ? "opacity-0" : ""
            }`}
          />
          <div
            className={`w-6 h-0.5 bg-black transition-all ${
              isMobileMenuOpen ? "-rotate-45 -translate-y-2" : ""
            }`}
          />
        </button>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="fixed md:hidden top-20 left-0 w-full bg-retroYellow shadow-lg transform transition-transform duration-300">
            <nav className="flex flex-col p-4">
              {navItems.map((item) => (
                <Link
                  key={item.name}
                  href={item.path}
                  className="py-3 text-black border-b border-gray-200 hover:text-retroGreen"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {item.name}
                </Link>
              ))}
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}
