import axios from "axios"

export default async function handler(req, res) {
  const { username } = req.query

  if (!username) {
    return res.status(400).json({ detail: "Username is required" })
  }

  try {
    const backendURL = `${process.env.NEXT_PUBLIC_BASE_API_URL}/get-metadata`
    const response = await axios.get(backendURL, { params: { username } })
    res.status(200).json(response.data)
  } catch (error) {
    console.error("Error fetching user metadata:", error.message)
    res.status(500).json({ detail: "Failed to fetch user metadata" })
  }
}
