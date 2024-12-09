import axios from "axios"

export default async function handler(req, res) {
  console.log("Received request at /api/update-metadata") // Log the request

  if (req.method === "PATCH") {
    try {
      const { username, metadata } = req.body
      console.log("Request Body:", { username, metadata }) // Log the incoming request body

      if (!username || !metadata) {
        console.error("Missing username or metadata in request body")
        return res
          .status(400)
          .json({ detail: "Username and metadata are required" })
      }

      const backendURL = `${process.env.NEXT_PUBLIC_BASE_API_URL}/update-metadata`
      console.log("Forwarding request to backend at:", backendURL) // Log where the request is going

      const response = await axios.patch(backendURL, { username, metadata })
      console.log("Backend Response:", response.data) // Log the backend response

      return res.status(200).json(response.data)
    } catch (error) {
      console.error(
        "Error in API route:",
        error.response?.data || error.message
      )
      return res
        .status(error.response?.status || 500)
        .json(error.response?.data || { detail: "Server error" })
    }
  } else {
    console.log(`Unsupported method: ${req.method}`) // Log unsupported HTTP methods
    res.setHeader("Allow", ["PATCH"])
    return res.status(405).end(`Method ${req.method} Not Allowed`)
  }
}
