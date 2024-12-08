// components/auth/auth.js
import { signIn } from "next-auth/react"

export async function login(username, password) {
  try {
    const result = await signIn("credentials", {
      redirect: false,
      username,
      password,
    })

    if (result.ok) {
      return { success: true }
    } else {
      return {
        success: false,
        error: result.error || "Invalid username or password.",
      }
    }
  } catch (error) {
    return { success: false, error: "An unexpected error occurred." }
  }
}
