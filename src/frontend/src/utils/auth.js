// src/utils/auth.js
export const getToken = () => localStorage.getItem("token")
export const setToken = (token) => {
  console.log("Setting token:", token) // Log the token to verify it's being set
  localStorage.setItem("token", token)
}
export const removeToken = () => localStorage.removeItem("token")
