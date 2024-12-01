// src/utils/api.js
export const getToken = () => {
  return localStorage.getItem("token") // Fetch the token from localStorage
}

export const fetchWithAuth = async (url, options = {}) => {
  const token = getToken() // Retrieve the token using getToken
  if (token) {
    options.headers = {
      ...options.headers,
      Authorization: `Bearer ${token}`, // Include the token in the headers
    }
  }

  try {
    const response = await fetch(url, options)
    return response
  } catch (err) {
    console.error("Error with fetch request:", err)
    throw err // Re-throw the error to be caught in the caller
  }
}
