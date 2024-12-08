import "./globals.css"
import { getServerSession } from "next-auth"
import { authOptions } from "./auth"
import ClientSessionProvider from "@/components/auth/ClientSessionProvider"
import SessionInit from "@/components/auth/SessionInit"
import Header from "@/components/layout/Header"
import Footer from "@/components/layout/Footer"

export const metadata = {
  title: "innit",
  description: "Let AI teach you practical language skills",
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <link href="assets/logo.png" rel="shortcut icon" type="image/x-icon" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, user-scalable=0, maximum-scale=1, minimum-scale=1"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600&family=Montserrat:wght@700&family=Playfair+Display:wght@400;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen">
        <ClientSessionProvider>
          <Header />
          <main>{children}</main>
          <Footer />
        </ClientSessionProvider>
      </body>
    </html>
  )
}
